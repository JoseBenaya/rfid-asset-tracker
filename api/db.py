import os
import sqlite3
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Ensure data directory exists
os.makedirs(os.path.dirname(config["db_path"]), exist_ok=True)

# Database setup
SQLALCHEMY_DATABASE_URL = f"sqlite:///{config['db_path']}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    asset_type = Column(String, index=True)
    status = Column(String, default="active")  # active, missing, idle
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scans = relationship("Scan", back_populates="asset", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    location = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rssi = Column(Integer, nullable=True)  # Signal strength (simulated)
    asset = relationship("Asset", back_populates="scans")

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database with sample data if it doesn't exist
def init_sample_data():
    if not os.path.exists(config["db_path"]) or os.path.getsize(config["db_path"]) == 0:
        init_db()
        db = SessionLocal()
        
        # Sample assets
        sample_assets = [
            Asset(tag_id="RF001", name="Laptop", description="Dell XPS 15", asset_type="Electronics"),
            Asset(tag_id="RF002", name="Projector", description="Epson PowerLite", asset_type="Electronics"),
            Asset(tag_id="RF003", name="Chair", description="Office chair", asset_type="Furniture"),
            Asset(tag_id="RF004", name="Monitor", description="Dell 27-inch", asset_type="Electronics"),
            Asset(tag_id="RF005", name="Keyboard", description="Logitech MX", asset_type="Electronics"),
        ]
        
        for asset in sample_assets:
            db.add(asset)
        
        db.commit()
        
        # Sample scans
        for asset in db.query(Asset).all():
            initial_scan = Scan(
                asset_id=asset.id,
                location="Office",
                rssi=-50
            )
            db.add(initial_scan)
        
        db.commit()
        db.close() 