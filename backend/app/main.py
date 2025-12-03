from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
import uuid
import pika
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

# RabbitMQ configuration
def get_rabbitmq_connection():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('project_one_rabbitmq'))
        return connection
    except Exception as e:
        print(f"RabbitMQ connection error: {e}")
        return None

def publish_to_queue(queue_name: str, message: dict) -> bool:
    """Publish message to RabbitMQ queue"""
    try:
        connection = get_rabbitmq_connection()
        if not connection:
            return False
            
        channel = connection.createChannel()
        
        # Declare queue as durable (survives broker restart)
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Publish with persistence
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Failed to publish to queue: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "Real-Time Data Backend API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/data", response_model=DataResponse)
async def create_data(data: DataCreate):
    """
    Receive data via POST and queue for processing
    """
    try:
        # Create message for queue
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "operation": "CREATE",
            "data": {
                "value": data.value,
                "data_type": data.data_type,
                "extra_data": data.extra_data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to queue
        if publish_to_queue("data-processing", message):
            return {
                "message_id": message_id,
                "status": "processing",
                "message": "Data queued for processing"
            }, 202
        else:
            # Fallback to direct processing if queue is unavailable
            return await create_data_direct(data)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error queuing data: {str(e)}")

async def create_data_direct(data: DataCreate, db: Session = Depends(get_db)):
    """
    Receive data via POST, save to database, and broadcast to all WebSocket clients
    """
    try:
        # Create new record
        db_record = DataRecord(
            value=data.value,
            data_type=data.data_type,
            extra_data=data.extra_data,
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
                "extra_data": db_record.extra_data,
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
