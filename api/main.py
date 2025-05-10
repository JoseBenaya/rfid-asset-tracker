import json
import asyncio
import logging
import os
import sys
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local modules
from db import get_db, Asset, Scan, init_sample_data
from mock_data import RFIDSimulator

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.get("log_level", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("asset_tracker_api")

# Initialize database with sample data
init_sample_data()

# Initialize RFID simulator
simulator = RFIDSimulator()

# WebSocket connections
active_connections: List[WebSocket] = []

# Pydantic models
class ScanRequest(BaseModel):
    tag_id: str
    location: str

class ScanResponse(BaseModel):
    tag_id: str
    location: str
    timestamp: str
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None

class AssetModel(BaseModel):
    id: int
    tag_id: str
    name: str
    description: Optional[str] = None
    asset_type: str
    status: str
    last_seen: Optional[str] = None
    last_location: Optional[str] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        try:
            if websocket.client_state.CONNECTED:
                await websocket.send_json(message)
        except Exception as e:
            logger.debug(f"Error sending WebSocket message to a client: {str(e)}")
            # Silent fail for individual client errors

    async def broadcast(self, message: dict):
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                if connection.client_state.CONNECTED:
                    await connection.send_json(message)
            except Exception as e:
                logger.debug(f"Removing disconnected client: {str(e)}")
                disconnected_clients.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected_clients:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

# Initialize connection manager
manager = ConnectionManager()

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the RFID simulator if enabled in config
    if config.get("simulate_auto_scan", False):
        # Create a DB session for the simulator
        db = next(get_db())
        simulator.db_session = db
        await simulator.start_simulation()
    
    yield  # This is where FastAPI runs
    
    # Shutdown: Stop the RFID simulator
    await simulator.stop_simulation()

# Create FastAPI app
app = FastAPI(title="RFID Asset Tracker API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
@app.get("/")
def read_root():
    return {"message": "RFID Asset Tracker API"}

@app.get("/api/assets", response_model=List[AssetModel])
def get_assets(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all assets with optional filtering by status"""
    query = db.query(Asset)
    
    if status:
        query = query.filter(Asset.status == status)
    
    assets = query.all()
    result = []
    
    for asset in assets:
        # Get the most recent scan for each asset
        last_scan = db.query(Scan).filter(Scan.asset_id == asset.id).order_by(Scan.timestamp.desc()).first()
        
        asset_data = {
            "id": asset.id,
            "tag_id": asset.tag_id,
            "name": asset.name,
            "description": asset.description,
            "asset_type": asset.asset_type,
            "status": asset.status,
            "last_seen": last_scan.timestamp.isoformat() if last_scan else None,
            "last_location": last_scan.location if last_scan else None
        }
        result.append(asset_data)
    
    return result

@app.get("/api/assets/{asset_id}", response_model=AssetModel)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get a specific asset by ID"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Get the most recent scan
    last_scan = db.query(Scan).filter(Scan.asset_id == asset.id).order_by(Scan.timestamp.desc()).first()
    
    return {
        "id": asset.id,
        "tag_id": asset.tag_id,
        "name": asset.name,
        "description": asset.description,
        "asset_type": asset.asset_type,
        "status": asset.status,
        "last_seen": last_scan.timestamp.isoformat() if last_scan else None,
        "last_location": last_scan.location if last_scan else None
    }

@app.get("/api/assets/{asset_id}/scans")
def get_asset_scans(asset_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Get the scan history for a specific asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    scans = db.query(Scan).filter(Scan.asset_id == asset_id).order_by(Scan.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": scan.id,
            "location": scan.location,
            "timestamp": scan.timestamp.isoformat(),
            "rssi": scan.rssi
        }
        for scan in scans
    ]

@app.post("/api/scan", response_model=ScanResponse)
async def create_scan(scan_request: ScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a manual scan event"""
    # Find the asset by tag ID
    asset = db.query(Asset).filter(Asset.tag_id == scan_request.tag_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset with this tag ID not found")
    
    # Create a new scan record
    new_scan = Scan(
        asset_id=asset.id,
        location=scan_request.location,
        rssi=random.randint(-70, -30)  # Simulated signal strength
    )
    db.add(new_scan)
    
    # Update asset status and timestamps
    asset.status = "active"
    asset.updated_at = datetime.utcnow()
    db.commit()
    
    # Generate scan event for WebSocket clients
    background_tasks.add_task(
        simulator.generate_specific_scan, 
        scan_request.tag_id, 
        scan_request.location
    )
    
    return {
        "tag_id": scan_request.tag_id,
        "location": scan_request.location,
        "timestamp": new_scan.timestamp.isoformat(),
        "asset_name": asset.name,
        "asset_type": asset.asset_type
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Define the callback function for scan events
        async def on_scan(scan_data):
            try:
                # Find asset information
                db = next(get_db())
                asset = db.query(Asset).filter(Asset.tag_id == scan_data["tag_id"]).first()
                if asset:
                    scan_data["asset_name"] = asset.name
                    scan_data["asset_type"] = asset.asset_type
                await manager.send_message(scan_data, websocket)
            except Exception as e:
                logger.error(f"Error in WebSocket callback: {str(e)}")
        
        # Subscribe to scan events
        subscriber_id = simulator.subscribe(on_scan)
        
        # Keep the connection open
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket)
        simulator.unsubscribe(subscriber_id)

# Mark assets as missing if not seen for a while
@app.get("/api/maintenance/update-status")
def update_asset_status(db: Session = Depends(get_db)):
    """Update asset statuses based on last seen time"""
    assets = db.query(Asset).all()
    now = datetime.utcnow()
    threshold = timedelta(hours=24)
    
    updated_count = 0
    for asset in assets:
        last_scan = db.query(Scan).filter(Scan.asset_id == asset.id).order_by(Scan.timestamp.desc()).first()
        if last_scan:
            time_since_last_scan = now - last_scan.timestamp
            
            # If not seen in 24 hours, mark as missing
            if time_since_last_scan > threshold and asset.status != "missing":
                asset.status = "missing"
                updated_count += 1
            # If seen recently but marked as missing, update to active
            elif time_since_last_scan <= threshold and asset.status == "missing":
                asset.status = "active"
                updated_count += 1
    
    db.commit()
    return {"message": f"Updated status for {updated_count} assets"}

# Run the API with uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.get("port", 8000), reload=True) 