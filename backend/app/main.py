from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime

from .database import engine, get_db
from .models import Base, DataRecord
from .schemas import DataCreate, DataResponse
from .websocket_manager import manager

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Data Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Real-Time Data Backend API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/data", response_model=DataResponse)
async def create_data(data: DataCreate, db: Session = Depends(get_db)):
    """
    Receive data via POST, save to database, and broadcast to all WebSocket clients
    """
    try:
        # Create new record
        db_record = DataRecord(
            value=data.value,
            data_type=data.data_type,
            metadata=data.metadata,
            timestamp=datetime.utcnow()
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        # Broadcast to all connected WebSocket clients
        broadcast_data = {
            "event": "data_update",
            "data": {
                "id": db_record.id,
                "value": db_record.value,
                "data_type": db_record.data_type,
                "metadata": db_record.metadata,
                "timestamp": db_record.timestamp.isoformat()
            }
        }
        await manager.broadcast(json.dumps(broadcast_data))
        
        return db_record
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")


@app.get("/api/data", response_model=List[DataResponse])
async def get_data(limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve recent data records
    """
    records = db.query(DataRecord).order_by(DataRecord.timestamp.desc()).limit(limit).all()
    return records


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data streaming
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
