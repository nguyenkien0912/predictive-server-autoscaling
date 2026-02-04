"""
Response models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class PredictionItem(BaseModel):
    """Single prediction item"""
    interval_minutes: int
    predicted_requests: float
    predicted_bytes: Optional[float] = None
    confidence: Optional[float] = None
    timestamp: str

class ForecastResponse(BaseModel):
    """Response model for forecast endpoint"""
    timestamp: str
    predictions: List[PredictionItem]
    status: str = "success"

class ScalingRecommendation(BaseModel):
    """Scaling recommendation details"""
    action: str = Field(..., description="scale-out, scale-in, or maintain")
    recommended_servers: int
    reason: str
    confidence: float = Field(..., ge=0, le=1)

class ScalingResponse(BaseModel):
    """Response model for scaling recommendation"""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    current_servers: int
    recommended_servers: int
    action: str
    reason: str
    confidence: float
    estimated_utilization: float
    estimated_cost_change: float
    details: Optional[Dict[str, Any]] = None

class DataPoint(BaseModel):
    """Single data point"""
    timestamp: str
    requests: float
    bytes: float
    errors: Optional[int] = 0

class HistoricalDataResponse(BaseModel):
    """Response model for historical data"""
    data: List[DataPoint]
    interval: str
    start_time: str
    end_time: str
    total_records: int
