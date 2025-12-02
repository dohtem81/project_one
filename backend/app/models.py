from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from .database import Base


class DataRecord(Base):
    """
    Database model for storing incoming data records
    """
    __tablename__ = "data_records"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float, nullable=False)
    data_type = Column(String, nullable=True)
    extra_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DataRecord(id={self.id}, value={self.value}, timestamp={self.timestamp})>"
