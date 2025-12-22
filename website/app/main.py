from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import os

from commonpackages.models import Base, DataRecord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/project_one_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# WebSocket gateway URL
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL', 'ws://localhost:8000/ws')

app = FastAPI(title="IoT Data Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "websocket_url": WEBSOCKET_URL
    })

@app.get("/api/ambient-history")
async def get_ambient_history(db: Session = Depends(get_db)):
    """Get last 15 minutes of ambient temperature data"""
    from datetime import datetime, timedelta
    from sqlalchemy import and_, func
    import json
    
    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)
    
    # Query ambient temperature data from last 15 minutes
    records = db.query(DataRecord).filter(
        and_(
            DataRecord.data_type == "temperature",
            DataRecord.timestamp >= fifteen_minutes_ago
        )
    ).order_by(DataRecord.timestamp).all()
    
    # Filter for ambient sensor only and format the data
    ambient_records = []
    for record in records:
        try:
            extra_data = json.loads(record.extra_data) if isinstance(record.extra_data, str) else record.extra_data
            if extra_data.get('name') == 'ambient':
                ambient_records.append({
                    'timestamp': record.timestamp.isoformat(),
                    'value': extra_data.get('value')
                })
        except:
            continue
    
    return {"data": ambient_records}

@app.get("/api/wheels-history")
async def get_wheels_history(db: Session = Depends(get_db)):
    """Get last 15 minutes of wheel temperature and vibration data"""
    from datetime import datetime, timedelta
    from sqlalchemy import and_, or_
    import json
    
    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)
    
    # Query temperature and vibration data from last 15 minutes
    records = db.query(DataRecord).filter(
        and_(
            or_(
                DataRecord.data_type == "temperature",
                DataRecord.data_type == "vibration"
            ),
            DataRecord.timestamp >= fifteen_minutes_ago
        )
    ).order_by(DataRecord.timestamp).all()
    
    # Organize data by sensor and type
    wheel_sensors = ['left_front_bearing', 'right_front_bearing', 'left_rear_bearing', 'right_rear_bearing']
    wheels_data = {sensor: {'temperature': [], 'vibration': []} for sensor in wheel_sensors}
    
    for record in records:
        try:
            extra_data = json.loads(record.extra_data) if isinstance(record.extra_data, str) else record.extra_data
            sensor_name = extra_data.get('name')
            
            if sensor_name in wheel_sensors:
                if record.data_type == 'temperature':
                    wheels_data[sensor_name]['temperature'].append({
                        'timestamp': record.timestamp.isoformat(),
                        'value': extra_data.get('value')
                    })
                elif record.data_type == 'vibration':
                    wheels_data[sensor_name]['vibration'].append({
                        'timestamp': record.timestamp.isoformat(),
                        'avg': extra_data.get('avg'),
                        'peak': extra_data.get('peak'),
                        'rms': extra_data.get('rms')
                    })
        except:
            continue
    
    return {"data": wheels_data}

@app.get("/api/data")
async def get_data(detailed: bool = False, type: str = "all", limit: int = 50, db: Session = Depends(get_db)):
    """API endpoint for data"""
    query_limit = limit if detailed else 50
    
    vibration_data = []
    temperature_data = []
    
    if type == "all" or type == "vibration":
        vibration_data = db.query(DataRecord).filter(DataRecord.data_type == "vibration").order_by(desc(DataRecord.timestamp)).limit(query_limit).all()
    
    if type == "all" or type == "temperature":
        temperature_data = db.query(DataRecord).filter(DataRecord.data_type == "temperature").order_by(desc(DataRecord.timestamp)).limit(query_limit).all()

    if detailed:
        # Return full records with IDs for detailed view
        return {
            "vibration": [{
                "id": record.id,
                "timestamp": record.timestamp.isoformat(),
                "data_type": record.data_type,
                "extra_data": record.extra_data
            } for record in vibration_data],
            "temperature": [{
                "id": record.id,
                "timestamp": record.timestamp.isoformat(),
                "data_type": record.data_type,
                "extra_data": record.extra_data
            } for record in temperature_data]
        }
    else:
        # Return broadcast dict for dashboard
        return {
            "vibration": [record.broadcast_dict() for record in vibration_data],
            "temperature": [record.broadcast_dict() for record in temperature_data]
        }