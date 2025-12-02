from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class DataCreate(BaseModel):
    """
    Schema for creating new data records via POST request
    """
    value: float
    data_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DataResponse(BaseModel):
    """
    Schema for data record responses
    """
    id: int
    value: float
    data_type: Optional[str]
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True  # Allows ORM model conversion
