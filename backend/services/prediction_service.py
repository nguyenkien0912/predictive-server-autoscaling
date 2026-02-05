"""
Prediction Service - Handles traffic forecasting using trained models
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import logging
import pickle

from models.response_models import PredictionItem

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for traffic prediction using XGBoost models"""
    
    def __init__(self, data_service=None):
        """Initialize prediction service and load models
        
        Args:
            data_service: Optional DataService instance for accessing historical data
        """
        self.data_service = data_service
        self.models = {}
        self.feature_names = [
            'hour', 'dayofweek', 'is_weekend', 'part_of_day',
            'hour_sin', 'hour_cos', 'lag_1', 'lag_2', 'lag_3',
            'rolling_mean', 'rolling_std', 'rolling_max'
        ]
        self._load_models()
        
    def _load_prediction_results(self) -> pd.DataFrame:
        """Load actual prediction results from CSV if available"""
        try:
            # Try multiple possible paths
            possible_paths = [
                '/app/data/prediction_results_5m.csv',  # Docker volume mount
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'prediction_results_5m.csv'),  # Local dev
            ]
            
            for csv_path in possible_paths:
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    logger.info(f"Loaded {len(df)} prediction results from {csv_path}")
                    return df
            
            logger.warning("prediction_results_5m.csv not found in any location")
            return None
        except Exception as e:
            logger.error(f"Error loading prediction results: {str(e)}")
            return None
    
    def _load_models(self):
        """Load trained LightGBM model for 5m predictions"""
        try:
            # Try multiple possible paths
            possible_paths = [
                '/app/data/best_model_lgbm_5m.pkl',  # Docker volume mount  
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'best_model_lgbm_5m.pkl'),  # Local dev
            ]
            
            for model_path in possible_paths:
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.models['5m'] = pickle.load(f)
                    logger.info(f"Loaded LightGBM model from {model_path}")
                    return
            
            logger.warning(f"Model file not found in any location")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
    
    def _create_features(self, timestamp: pd.Timestamp, lag_data: Optional[List[float]] = None) -> Dict:
        """Create features for model input"""
        features = {}
        
        # Time-based features
        features['hour'] = timestamp.hour
        features['minute'] = timestamp.minute  # Thêm minute cho variation
        features['dayofweek'] = timestamp.dayofweek
        features['is_weekend'] = 1 if timestamp.dayofweek >= 5 else 0
        
        # Part of day (0=night, 1=morning, 2=afternoon, 3=evening)
        if 0 <= timestamp.hour < 6:
            features['part_of_day'] = 0
        elif 6 <= timestamp.hour < 12:
            features['part_of_day'] = 1
        elif 12 <= timestamp.hour < 18:
            features['part_of_day'] = 2
        else:
            features['part_of_day'] = 3
        
        # Cyclical encoding
        features['hour_sin'] = np.sin(2 * np.pi * timestamp.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * timestamp.hour / 24)
        
        # Lag features - GET FROM REAL DATA
        if lag_data and len(lag_data) >= 3:
            features['lag_1'] = lag_data[-1]
            features['lag_2'] = lag_data[-2]
            features['lag_3'] = lag_data[-3]
            
            # Rolling statistics
            features['rolling_mean'] = np.mean(lag_data[-3:])
            features['rolling_std'] = np.std(lag_data[-3:])
            features['rolling_max'] = np.max(lag_data[-3:])
        else:
            # Get LAG from actual historical data (not synthetic!)
            if self.data_service and self.data_service.data_1m is not None:
                try:
                    # Remove timezone if present
                    ts = timestamp
                    if ts.tz is not None:
                        ts = ts.tz_localize(None)
                    
                    # Get previous 3 data points from real data
                    data_df = self.data_service.data_1m
                    data_index = data_df.index
                    if hasattr(data_index, 'tz') and data_index.tz is not None:
                        data_index = data_index.tz_localize(None)
                    
                    # Find index position closest to current timestamp
                    time_diffs = abs(data_index - ts)
                    closest_idx = time_diffs.argmin()
                    
                    # Get 3 previous values (lag_1, lag_2, lag_3)
                    if closest_idx >= 3:
                        lag_values = data_df.iloc[closest_idx-3:closest_idx]['requests'].values
                        if len(lag_values) >= 3:
                            features['lag_3'] = float(lag_values[0])
                            features['lag_2'] = float(lag_values[1])
                            features['lag_1'] = float(lag_values[2])
                            
                            # Rolling statistics from real data
                            features['rolling_mean'] = np.mean(lag_values)
                            features['rolling_std'] = np.std(lag_values)
                            features['rolling_max'] = np.max(lag_values)
                            logger.info(f"Using REAL lag data: lag_1={features['lag_1']:.2f}, lag_2={features['lag_2']:.2f}, lag_3={features['lag_3']:.2f}")
                        else:
                            raise ValueError("Not enough lag values")
                    else:
                        raise ValueError("Not enough historical data points")
                        
                except Exception as e:
                    logger.warning(f"Could not get real lag data: {str(e)}, using fallback")
                    # Fallback: use current traffic
                    current_pattern = self.get_current_traffic(timestamp.isoformat())
                    features['lag_1'] = current_pattern
                    features['lag_2'] = current_pattern
                    features['lag_3'] = current_pattern
                    features['rolling_mean'] = current_pattern
                    features['rolling_std'] = 0
                    features['rolling_max'] = current_pattern
            else:
                # No data service - use current traffic as fallback
                current_pattern = self.get_current_traffic(timestamp.isoformat())
                features['lag_1'] = current_pattern
                features['lag_2'] = current_pattern
                features['lag_3'] = current_pattern
                features['rolling_mean'] = current_pattern
                features['rolling_std'] = 0
                features['rolling_max'] = current_pattern
        
        return features
    
    def _predict_with_model(self, features: Dict, interval: str, steps_ahead: int = 1) -> float:
        """
        Make prediction using ML model if available, otherwise use pattern-based prediction
        """
        # Try to use ML model if available
        if '5m' in self.models:
            try:
                base_prediction = self._predict_with_ml_model(features)
                
                # Apply interval-specific deterministic adjustments for different time horizons
                if interval == '1m':
                    prediction = base_prediction * 0.99
                elif interval == '5m':
                    prediction = base_prediction
                else:  # 15m
                    trend_factor = 1.0 + (steps_ahead - 1) * 0.01
                    prediction = base_prediction * trend_factor * 1.05
                
                logger.info(f"ML model prediction ({interval}): {prediction:.2f} req/min")
                return max(0, float(prediction))
            except Exception as e:
                logger.warning(f"ML model prediction failed, using pattern-based: {str(e)}")
        
        # Fallback to pattern-based prediction
        return self._predict_with_pattern(features, interval, steps_ahead)
    
    def _predict_with_ml_model(self, features: Dict) -> float:
        """
        Make prediction using ONLY trained ML model
        """
        if '5m' not in self.models:
            raise ValueError("LightGBM model not available")
        
        try:
            # Convert features to DataFrame
            X = pd.DataFrame([features])[self.feature_names]
            
            # Make prediction with model
            prediction = self.models['5m'].predict(X)[0]
            return max(0, float(prediction))
            
        except Exception as e:
            logger.error(f"Error with ML model prediction: {str(e)}")
            raise
    
    def _predict_with_pattern(self, features: Dict, interval: str, steps_ahead: int = 1) -> float:
        """
        Pattern-based prediction when ML model is not available
        Uses recent traffic (lag features) as primary signal with small trend adjustments
        """
        hour = features.get('hour', 12)
        minute = features.get('minute', 0)
        dayofweek = features.get('dayofweek', 0)
        
        # Primary signal: Use recent traffic from lag features
        if 'lag_1' in features and features['lag_1'] > 0:
            # Start with most recent traffic
            base_prediction = features['lag_1']
            
            # Calculate short-term trend from recent lags
            if 'lag_2' in features and 'lag_3' in features:
                recent_trend = (features['lag_1'] - features['lag_3']) / 2
            else:
                recent_trend = 0
            
            # Small time-based adjustment (much smaller than before)
            time_factor = 1.0
            if 9 <= hour <= 17:  # Business hours - slight increase
                time_factor = 1.05
            elif hour < 6 or hour > 22:  # Night hours - slight decrease  
                time_factor = 0.95
            
            # Weekend reduction (smaller factor)
            if dayofweek >= 5:
                time_factor *= 0.9
            
            # Combine base + trend + time adjustment
            prediction = base_prediction * time_factor + recent_trend * 0.3
            
        else:
            # Fallback when no lag data (shouldn't happen in practice)
            if 9 <= hour <= 17:
                prediction = 100
            elif 6 <= hour <= 22:
                prediction = 60
            else:
                prediction = 30
        
        # Interval-specific adjustments (very small)
        if interval == '1m':
            # 1 minute ahead - almost no change
            prediction = prediction * 1.0 + np.random.normal(0, 2)
        elif interval == '5m':
            # 5 minutes ahead - slight extrapolation
            prediction = prediction * 1.02 + recent_trend * 0.5
        else:  # 15m
            # 15 minutes ahead - more trend influence
            prediction = prediction * 1.05 + recent_trend * 1.5
        
        logger.info(f"Pattern-based prediction ({interval}): {prediction:.2f} req/min (lag_1: {features.get('lag_1', 'N/A')})")
        return max(10, min(500, prediction))
    
    def get_current_traffic(self, current_time: str) -> float:
        """
        Get current traffic from actual data service
        
        Args:
            current_time: Current timestamp
            
        Returns:
            Current request rate (requests per minute)
        """
        try:
            # Try to get actual data from data service
            current_ts = pd.Timestamp(current_time)
            # Remove timezone info if present to match data index
            if current_ts.tz is not None:
                current_ts = current_ts.tz_localize(None)
            
            # Get data from data_service (1-minute interval)
            if self.data_service and self.data_service.data_1m is not None:
                # Ensure data index is also timezone-naive
                data_index = self.data_service.data_1m.index
                if hasattr(data_index, 'tz') and data_index.tz is not None:
                    data_index = data_index.tz_localize(None)
                
                # Find nearest timestamp in data
                if current_ts in data_index:
                    return float(self.data_service.data_1m.loc[current_ts, 'requests'])
                else:
                    # Find closest timestamp (within 5 minutes)
                    time_diffs = abs(data_index - current_ts)
                    closest_idx = time_diffs.argmin()
                    
                    # Check if closest timestamp is within 5 minutes
                    if time_diffs[closest_idx] < pd.Timedelta(minutes=5):
                        return float(self.data_service.data_1m.iloc[closest_idx]['requests'])
            
            # Fallback: generate realistic pattern if no data available
            logger.warning(f"No data found for {current_time}, using fallback pattern")
            hour = current_ts.hour
            dayofweek = current_ts.dayofweek
            
            if 9 <= hour <= 17:
                base = 35 + 20 * np.sin(np.pi * (hour - 9) / 8)
            elif 6 <= hour <= 22:
                base = 25 + 10 * np.sin(np.pi * (hour - 6) / 16)
            else:
                base = 12 + 5 * np.sin(np.pi * hour / 12)
            
            if dayofweek >= 5:
                base *= 0.65
            
            return max(5, base + np.random.normal(0, base * 0.15))
            
        except Exception as e:
            logger.error(f"Error getting current traffic: {str(e)}")
            return 30.0  # Safe fallback
    
    def predict(
        self,
        current_time: str,
        intervals: List[int] = [1, 5, 15],
        lag_data: Optional[List[float]] = None
    ) -> List[PredictionItem]:
        """
        Make traffic predictions for specified intervals
        
        Args:
            current_time: Current timestamp (ISO format)
            intervals: List of forecast intervals in minutes
            lag_data: Recent historical data for lag features
            
        Returns:
            List of PredictionItem objects with future forecasts
        """
        predictions = []
        
        try:
            current_ts = pd.Timestamp(current_time)
            
            # No need to update recent_history - we get lag from real data
            
            for interval in intervals:
                # Calculate future timestamp for time-based features
                future_ts = current_ts + timedelta(minutes=interval)
                
                # Create features: TIME features from FUTURE, LAG features from CURRENT
                # Get lag data from CURRENT timestamp (not future!)
                features_current = self._create_features(current_ts, lag_data)
                
                # Update time features to future (but keep lag features from current)
                features = features_current.copy()
                features['hour'] = future_ts.hour
                features['minute'] = future_ts.minute
                features['dayofweek'] = future_ts.dayofweek
                features['is_weekend'] = 1 if future_ts.dayofweek >= 5 else 0
                
                # Part of day for future timestamp
                if 0 <= future_ts.hour < 6:
                    features['part_of_day'] = 0
                elif 6 <= future_ts.hour < 12:
                    features['part_of_day'] = 1
                elif 12 <= future_ts.hour < 18:
                    features['part_of_day'] = 2
                else:
                    features['part_of_day'] = 3
                
                # Cyclical encoding for future hour
                features['hour_sin'] = np.sin(2 * np.pi * future_ts.hour / 24)
                features['hour_cos'] = np.cos(2 * np.pi * future_ts.hour / 24)
                
                # Determine model interval
                if interval <= 1:
                    model_interval = '1m'
                elif interval <= 5:
                    model_interval = '5m'
                else:
                    model_interval = '15m'
                
                # Calculate steps ahead for trend analysis
                steps_ahead = max(1, interval // 5)  # Convert to 5-min steps
                
                # Make FUTURE prediction
                predicted_requests = self._predict_with_model(features, model_interval, steps_ahead)
                
                # Estimate bytes (roughly 20KB per request with variation)
                avg_bytes = np.random.uniform(15000, 25000)
                predicted_bytes = predicted_requests * avg_bytes
                
                # Calculate confidence based on prediction horizon
                base_confidence = 0.95
                horizon_penalty = min(0.3, interval * 0.01)  # Reduce confidence for longer horizons
                confidence = max(0.6, base_confidence - horizon_penalty)
                
                predictions.append(PredictionItem(
                    interval_minutes=interval,
                    predicted_requests=round(predicted_requests, 2),
                    predicted_bytes=round(predicted_bytes, 2),
                    confidence=round(confidence, 3),
                    timestamp=future_ts.isoformat()
                ))
            
            logger.info(f"Generated {len(predictions)} FUTURE predictions for {current_time}")
            
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            raise
        
        return predictions
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            "loaded_models": list(self.models.keys()),
            "features": self.feature_names,
            "intervals_supported": ["1m", "5m", "15m"]
        }