import json
import random
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.get("log_level", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mock_rfid")

class RFIDSimulator:
    """
    Simulates RFID scanning events for testing and demonstration purposes
    """
    
    def __init__(self, db_session=None):
        self.locations = config.get("default_locations", ["Office", "Warehouse", "Meeting Room"])
        self.db_session = db_session
        self.running = False
        self.scan_task = None
        self.subscribers = []
    
    async def start_simulation(self):
        """Start automatic scan simulation"""
        if self.running:
            return
            
        self.running = True
        scan_interval = config.get("scan_interval_seconds", 5)
        logger.info(f"Starting RFID simulation with interval {scan_interval}s")
        
        # Create an async task for auto-scanning
        self.scan_task = asyncio.create_task(self._auto_scan_loop(scan_interval))
        
    async def stop_simulation(self):
        """Stop automatic scan simulation"""
        if not self.running:
            return
            
        self.running = False
        if self.scan_task:
            self.scan_task.cancel()
            try:
                await self.scan_task
            except asyncio.CancelledError:
                pass
            self.scan_task = None
        logger.info("Stopped RFID simulation")
    
    async def _auto_scan_loop(self, interval: int):
        """Run automated scan simulation at specified intervals"""
        try:
            while self.running:
                await self.generate_random_scan()
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("Auto-scan task cancelled")
            raise
    
    def subscribe(self, callback):
        """Subscribe to scan events"""
        self.subscribers.append(callback)
        return len(self.subscribers) - 1
    
    def unsubscribe(self, index):
        """Unsubscribe from scan events"""
        if 0 <= index < len(self.subscribers):
            self.subscribers.pop(index)
    
    async def notify_subscribers(self, scan_data):
        """Notify all subscribers of new scan data"""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(scan_data)
                else:
                    callback(scan_data)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {str(e)}")
    
    async def generate_random_scan(self) -> Dict[str, Any]:
        """
        Generate a random RFID scan event
        """
        # If we have a database session, use real tag IDs
        tag_ids = []
        if self.db_session:
            from .db import Asset
            assets = self.db_session.query(Asset).all()
            tag_ids = [asset.tag_id for asset in assets]
        
        # Fallback to mock IDs if no database or empty
        if not tag_ids:
            tag_ids = [f"RF{i:03d}" for i in range(1, 6)]
        
        # Create scan data
        scan_data = {
            "tag_id": random.choice(tag_ids),
            "location": random.choice(self.locations),
            "timestamp": datetime.utcnow().isoformat(),
            "rssi": random.randint(-70, -30),  # Simulated signal strength
        }
        
        logger.debug(f"Generated mock scan: {scan_data}")
        await self.notify_subscribers(scan_data)
        return scan_data
    
    async def generate_specific_scan(self, tag_id: str, location: str) -> Dict[str, Any]:
        """
        Generate a scan event for a specific tag and location
        """
        scan_data = {
            "tag_id": tag_id,
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "rssi": random.randint(-70, -30),  # Simulated signal strength
        }
        
        logger.info(f"Generated specific scan: {scan_data}")
        await self.notify_subscribers(scan_data)
        return scan_data 