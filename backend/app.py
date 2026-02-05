"""
Predictive Server Autoscaling - Backend API
FastAPI server providing forecasting and autoscaling recommendations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
import uvicorn
from datetime import datetime, timedelta
import logging
import time

from services.data_service import DataService
from services.prediction_service import PredictionService
from services.autoscaling_service import AutoscalingService
from models.request_models import ForecastRequest, ScalingRequest
from models.response_models import ForecastResponse, ScalingResponse, HistoricalDataResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simulated time tracking for demo purposes
# Advances 1 NASA minute every 5 real seconds to show data variation
SIMULATION_START_TIME = datetime(1995, 8, 25, 6, 0, 0)  # Start at 6 AM
SIMULATION_START_REAL = time.time()  # Real time when simulation started
SIMULATION_SPEED = 12  # 1 real second = 12 simulated seconds (5 real sec = 1 min)

def get_simulated_time() -> str:
    """
    Get current simulated time in NASA dataset.
    Advances 1 minute every 5 real seconds for visible data variation.
    """
    elapsed_real_seconds = time.time() - SIMULATION_START_REAL
    elapsed_simulated_seconds = elapsed_real_seconds * SIMULATION_SPEED
    
    simulated_time = SIMULATION_START_TIME + timedelta(seconds=elapsed_simulated_seconds)
    
    # Wrap around after 24 hours (keep within August 25, 1995)
    if simulated_time.day != SIMULATION_START_TIME.day:
        hours_elapsed = (simulated_time - SIMULATION_START_TIME).total_seconds() / 3600
        hours_in_day = hours_elapsed % 24
        simulated_time = SIMULATION_START_TIME + timedelta(hours=hours_in_day)
    
    return simulated_time.strftime("%Y-%m-%dT%H:%M:%S")

# Initialize FastAPI app
app = FastAPI(
    title="Predictive Server Autoscaling API",
    description="API for traffic forecasting and autoscaling recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_service = DataService()
prediction_service = PredictionService(data_service=data_service)
autoscaling_service = AutoscalingService()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Predictive Server Autoscaling API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "data_service": "ok",
            "prediction_service": "ok",
            "autoscaling_service": "ok"
        }
    }

@app.get("/api/current-traffic")
async def get_current_traffic():
    """Get current traffic load from historical data (mapped to NASA 1995 test period)"""
    try:
        # Get simulated time (advances 1 minute every 5 real seconds)
        current_time_1995 = get_simulated_time()
        current_traffic = prediction_service.get_current_traffic(current_time_1995)
        
        logger.info(f"Current traffic at {current_time_1995}: {current_traffic:.2f} req/min")
        
        return JSONResponse({
            "timestamp": current_time_1995,
            "current_requests": round(current_traffic, 2)
        })
    except Exception as e:
        logger.error(f"Error getting current traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forecast", response_model=ForecastResponse)
async def forecast(request: ForecastRequest):
    """
    Predict future traffic for specified time windows
    
    Args:
        request: ForecastRequest containing current_time and intervals
        
    Returns:
        ForecastResponse with predictions for 1m, 5m, 15m intervals
    """
    try:
        logger.info(f"Forecast request received for time: {request.current_time}")
        
        # Get predictions from service
        predictions = prediction_service.predict(
            current_time=request.current_time,
            intervals=request.intervals or [1, 5, 15]
        )
        
        return ForecastResponse(
            timestamp=request.current_time,
            predictions=predictions,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error in forecast endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend-scaling", response_model=ScalingResponse)
async def recommend_scaling(request: ScalingRequest):
    """
    Get autoscaling recommendations based on current and predicted traffic
    
    Args:
        request: ScalingRequest with current metrics and predictions
        
    Returns:
        ScalingResponse with scaling recommendations
    """
    try:
        logger.info(f"Scaling recommendation request for {request.current_servers} servers")
        
        # Get scaling recommendation
        recommendation = autoscaling_service.recommend(
            current_servers=request.current_servers,
            current_load=request.current_load,
            predicted_load=request.predicted_load,
            current_utilization=request.current_utilization
        )
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Error in recommend-scaling endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/historical-data", response_model=HistoricalDataResponse)
async def get_historical_data(
    start_time: str = None,
    end_time: str = None,
    interval: str = "5m",
    limit: int = 1000
):
    """
    Get historical traffic data
    
    Args:
        start_time: Start timestamp (ISO format)
        end_time: End timestamp (ISO format)
        interval: Time interval (1m, 5m, 15m)
        limit: Maximum number of records
        
    Returns:
        HistoricalDataResponse with traffic data
    """
    try:
        logger.info(f"Historical data request: interval={interval}, limit={limit}")
        
        data = data_service.get_historical_data(
            start_time=start_time,
            end_time=end_time,
            interval=interval,
            limit=limit
        )
        
        return data
        
    except Exception as e:
        logger.error(f"Error in historical-data endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/summary")
async def get_metrics_summary():
    """Get summary of key metrics"""
    try:
        summary = {
            "total_records": data_service.get_total_records(),
            "date_range": data_service.get_date_range(),
            "intervals_available": ["1m", "5m", "15m"],
            "model_info": prediction_service.get_model_info()
        }
        return summary
    except Exception as e:
        logger.error(f"Error in metrics summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/autoscaling/config")
async def get_autoscaling_config():
    """Get current autoscaling configuration"""
    try:
        config = autoscaling_service.get_config()
        return config
    except Exception as e:
        logger.error(f"Error getting autoscaling config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cost/summary")
async def get_cost_summary(hours: int = 24):
    """Get accurate cost summary with time-weighted calculations"""
    try:
        cost_summary = autoscaling_service.cost_tracker.get_cost_summary(hours_back=hours)
        scaling_history = autoscaling_service.cost_tracker.get_scaling_history()
        
        return {
            "summary": cost_summary,
            "scaling_history": scaling_history[-10:],  # Last 10 events
            "cost_per_server_per_hour": autoscaling_service.config['cost_per_server_per_hour']
        }
    except Exception as e:
        logger.error(f"Error getting cost summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting Predictive Server Autoscaling API...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
