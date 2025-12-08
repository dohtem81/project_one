from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
import pika
import os
from datetime import datetime

from .database import engine, get_db
from commonpackages.models import Base, DataRecord
from .schemas import DataCreate, DataResponse
from .websocket_manager import manager

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Data Gateway")

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
        credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', 'admin'),
            os.getenv('RABBITMQ_PASSWORD', 'admin')
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
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
            
        channel = connection.channel()
        
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
    return {"message": "Real-Time Data Gateway API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/data", status_code=202)
async def create_data(data: DataCreate):
    """
    Receive data from IoT device and publish to RabbitMQ queue
    Arduino POSTs here, we queue it for processing
    Returns 202 Accepted (message queued for processing)
    """
    try:
        message = {
            "value": data.value,
            "data_type": data.data_type,
            "extra_data": data.extra_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to RabbitMQ for async processing
        success = publish_to_queue("iot-data", message)
        
        if not success:
            raise HTTPException(status_code=503, detail="Queue service unavailable")
        
        return {"status": "accepted", "message": "Data queued for processing"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error queuing data: {str(e)}")

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
