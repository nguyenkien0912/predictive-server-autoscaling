"""
Data Service - Handles loading and processing of historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os
import logging

from models.response_models import HistoricalDataResponse, DataPoint

logger = logging.getLogger(__name__)

class DataService:
    """Service for managing historical traffic data"""
    
    def __init__(self):
        """Initialize data service and load data"""
        self.data_1m = None
        self.data_5m = None
        self.data_15m = None
        self._load_data()
    
    def _load_data(self):
        """Load preprocessed data from parquet file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'nasa_logs_processed.parquet')
            
            if not os.path.exists(data_path):
                logger.warning(f"Data file not found: {data_path}. Creating dummy data.")
                self._create_dummy_data()
                return
            
            logger.info("Loading data from parquet file...")
            df = pd.read_parquet(data_path)
            
            # Resample to different intervals
            self.data_1m = self._resample_data(df, '1min')
            self.data_5m = self._resample_data(df, '5min')
            self.data_15m = self._resample_data(df, '15min')
            
            logger.info(f"Data loaded successfully: 1m={len(self.data_1m)}, 5m={len(self.data_5m)}, 15m={len(self.data_15m)}")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            self._create_dummy_data()
    
    def _resample_data(self, df, window):
        """Resample data to specified time window - simplified version"""
        try:
            # Simplified approach - just group by time window
            resampled = df.resample(window).agg({
                'host': 'count',
                'bytes': 'sum'
            })
            resampled.columns = ['requests', 'total_bytes']
            resampled['errors'] = 0  # Add errors column with default 0
            resampled = resampled.fillna(0)
            return resampled
        except Exception as e:
            logger.error(f"Error resampling data with window {window}: {str(e)}")
            # Return empty DataFrame on error
            empty_df = pd.DataFrame(columns=['requests', 'total_bytes', 'errors'])
            return empty_df
    
    def _create_dummy_data(self):
        """Create dummy data for testing"""
        logger.info("Creating dummy data for testing...")
        
        # Create date range
        start_date = pd.Timestamp('1995-07-01')
        end_date = pd.Timestamp('1995-08-31')
        
        # Generate time series
        dates_1m = pd.date_range(start=start_date, end=end_date, freq='1min')
        dates_5m = pd.date_range(start=start_date, end=end_date, freq='5min')
        dates_15m = pd.date_range(start=start_date, end=end_date, freq='15min')
        
        # Generate dummy traffic data with daily and hourly patterns
        def generate_traffic(dates):
            np.random.seed(42)
            traffic = []
            for date in dates:
                # Base load
                base = 100
                # Daily pattern (higher during weekdays)
                daily = 50 if date.dayofweek < 5 else 30
                # Hourly pattern (higher during business hours)
                hourly = 80 * np.sin(np.pi * (date.hour - 6) / 12) if 6 <= date.hour <= 18 else 20
                # Random noise
                noise = np.random.normal(0, 20)
                
                requests = max(0, base + daily + hourly + noise)
                traffic.append({
                    'requests': requests,
                    'total_bytes': requests * np.random.uniform(1000, 50000),
                    'errors': int(requests * 0.01)
                })
            return pd.DataFrame(traffic, index=dates)
        
        self.data_1m = generate_traffic(dates_1m)
        self.data_5m = generate_traffic(dates_5m)
        self.data_15m = generate_traffic(dates_15m)
    
    def get_historical_data(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        interval: str = "5m",
        limit: int = 1000
    ) -> HistoricalDataResponse:
        """
        Get historical traffic data
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            interval: Time interval (1m, 5m, 15m)
            limit: Maximum records to return
            
        Returns:
            HistoricalDataResponse with data
        """
        # Select appropriate dataset
        if interval == "1m":
            data = self.data_1m
        elif interval == "15m":
            data = self.data_15m
        else:
            data = self.data_5m
        
        if data is None or len(data) == 0:
            return HistoricalDataResponse(
                data=[],
                interval=interval,
                start_time="",
                end_time="",
                total_records=0
            )
        
        # Filter by time range
        if start_time:
            data = data[data.index >= pd.Timestamp(start_time)]
        if end_time:
            data = data[data.index <= pd.Timestamp(end_time)]
        
        # Limit results
        data = data.tail(limit)
        
        # Convert to response format
        data_points = [
            DataPoint(
                timestamp=idx.isoformat(),
                requests=float(row['requests']),
                bytes=float(row['total_bytes']),
                errors=int(row.get('errors', 0))
            )
            for idx, row in data.iterrows()
        ]
        
        return HistoricalDataResponse(
            data=data_points,
            interval=interval,
            start_time=data.index[0].isoformat() if len(data) > 0 else "",
            end_time=data.index[-1].isoformat() if len(data) > 0 else "",
            total_records=len(data_points)
        )
    
    def get_data_at_time(self, timestamp: str, interval: str = "5m") -> Optional[Dict]:
        """Get data point at specific time"""
        if interval == "1m":
            data = self.data_1m
        elif interval == "15m":
            data = self.data_15m
        else:
            data = self.data_5m
        
        if data is None:
            return None
        
        try:
            ts = pd.Timestamp(timestamp)
            if ts in data.index:
                row = data.loc[ts]
                return {
                    'requests': float(row['requests']),
                    'bytes': float(row['total_bytes']),
                    'errors': int(row.get('errors', 0))
                }
        except Exception as e:
            logger.error(f"Error getting data at time: {str(e)}")
        
        return None
    
    def get_total_records(self) -> int:
        """Get total number of records"""
        if self.data_5m is not None:
            return len(self.data_5m)
        return 0
    
    def get_date_range(self) -> Dict[str, str]:
        """Get date range of available data"""
        if self.data_5m is not None and len(self.data_5m) > 0:
            return {
                "start": self.data_5m.index[0].isoformat(),
                "end": self.data_5m.index[-1].isoformat()
            }
        return {"start": "", "end": ""}
