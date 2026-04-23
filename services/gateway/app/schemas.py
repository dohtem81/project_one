from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class DataCreate(BaseModel):
    """
    Schema for creating new data records via POST request
    """
    data_type: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class DataResponse(BaseModel):
    """
    Schema for data record responses
    """
    id: int
    data_type: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True  # Allows ORM model conversion
