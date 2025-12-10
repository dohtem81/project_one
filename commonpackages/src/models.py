from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DataRecord(Base):
    """Database model for storing incoming data records"""
    __tablename__ = "data_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data_type = Column(String, nullable=True)
    extra_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DataRecord(id={self.id}, data_type={self.data_type}, timestamp={self.timestamp})>"
    
    def broadcast_dict(self):
        return {
            "data_type": self.data_type,
            "extra_data": self.extra_data,
        }