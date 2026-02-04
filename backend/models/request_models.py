"""
Request models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ForecastRequest(BaseModel):
    """Request model for forecast endpoint"""
    current_time: str = Field(..., description="Current timestamp in ISO format")
    intervals: Optional[List[int]] = Field(default=[1, 5, 15], description="Time intervals in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_time": "1995-08-23T10:30:00",
                "intervals": [1, 5, 15]
            }
        }

class ScalingRequest(BaseModel):
    """Request model for scaling recommendation endpoint"""
    current_servers: int = Field(..., ge=1, description="Current number of servers")
    current_load: float = Field(..., ge=0, description="Current request load")
    predicted_load: float = Field(..., ge=0, description="Predicted request load")
    current_utilization: Optional[float] = Field(default=None, ge=0, le=100, description="Current utilization %")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_servers": 5,
                "current_load": 1500.0,
                "predicted_load": 2000.0,
                "current_utilization": 75.5
            }
        }
