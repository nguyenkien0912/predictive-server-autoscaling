"""Model package initialization"""

from .request_models import ForecastRequest, ScalingRequest
from .response_models import (
    ForecastResponse, 
    ScalingResponse, 
    HistoricalDataResponse,
    PredictionItem,
    DataPoint
)

__all__ = [
    'ForecastRequest',
    'ScalingRequest',
    'ForecastResponse',
    'ScalingResponse',
    'HistoricalDataResponse',
    'PredictionItem',
    'DataPoint'
]
