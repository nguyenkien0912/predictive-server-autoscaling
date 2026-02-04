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
    
    def __init__(self):
        """Initialize prediction service and load models"""
        self.models = {}
        self.feature_names = [
            'hour', 'dayofweek', 'is_weekend', 'part_of_day',
            'hour_sin', 'hour_cos', 'lag_1', 'lag_2', 'lag_3',
            'rolling_mean', 'rolling_std', 'rolling_max'
        ]
        self._load_models()
        self.historical_data = []  # Store recent data for lag features
        self.prediction_cache = self._load_prediction_results()  # Load actual predictions
        self.current_data_index = 0  # Track current position in dataset
        self.recent_history = []  # Store recent actual traffic for trend analysis
        
    def _load_prediction_results(self) -> pd.DataFrame:
        """Load actual prediction results from CSV if available"""
        try:
            csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'prediction_results_5m.csv')
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                logger.info(f"Loaded {len(df)} prediction results from CSV")
                return df
            else:
                logger.warning("prediction_results_5m.csv not found")
                return None
        except Exception as e:
            logger.error(f"Error loading prediction results: {str(e)}")
            return None
    
    def _load_models(self):
        """Load trained LightGBM model for 5m predictions"""
        try:
            models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            model_path = os.path.join(models_dir, 'best_model_lgbm_5m.pkl')
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models['5m'] = pickle.load(f)
                logger.info(f"Loaded LightGBM model from {model_path}")
            else:
                logger.warning(f"Model file not found: {model_path}")
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
        
        # Lag features
        if lag_data and len(lag_data) >= 3:
            features['lag_1'] = lag_data[-1]
            features['lag_2'] = lag_data[-2]
            features['lag_3'] = lag_data[-3]
            
            # Rolling statistics
            features['rolling_mean'] = np.mean(lag_data[-3:])
            features['rolling_std'] = np.std(lag_data[-3:])
            features['rolling_max'] = np.max(lag_data[-3:])
        else:
            # Generate realistic lag values based on current traffic pattern
            current_pattern = self.get_current_traffic(timestamp.isoformat())
            # Use deterministic variations instead of random
            features['lag_1'] = current_pattern * 0.98  # -2% for previous period
            features['lag_2'] = current_pattern * 0.95  # -5% for 2 periods ago
            features['lag_3'] = current_pattern * 0.92  # -8% for 3 periods ago
            features['rolling_mean'] = (features['lag_1'] + features['lag_2'] + features['lag_3']) / 3
            features['rolling_std'] = np.std([features['lag_1'], features['lag_2'], features['lag_3']])
            features['rolling_max'] = max(features['lag_1'], features['lag_2'], features['lag_3'])
        
        return features
    
    def _predict_with_model(self, features: Dict, interval: str, steps_ahead: int = 1) -> float:
        """
        Make prediction using ONLY trained ML model with interval adjustments
        """
        if '5m' not in self.models:
            raise ValueError("ML model not loaded. Cannot make predictions without trained model.")
        
        try:
            # Use ONLY trained LightGBM model
            base_prediction = self._predict_with_ml_model(features)
            
            # Apply interval-specific deterministic adjustments for different time horizons
            if interval == '1m':
                # 1-minute: More accurate, less uncertainty
                prediction = base_prediction * 0.99  # Slight adjustment for shorter interval
            elif interval == '5m':
                # 5-minute: Base model output (this is what model was trained for)
                prediction = base_prediction
            else:  # 15m
                # 15-minute: More uncertainty, potential trend effects
                trend_factor = 1.0 + (steps_ahead - 1) * 0.01  # +1% per additional step
                prediction = base_prediction * trend_factor * 1.05  # Slight increase for longer horizon
            
            logger.info(f"ML model prediction ({interval}): {prediction:.2f} req/min (base: {base_prediction:.2f})")
            return max(0, float(prediction))
        except Exception as e:
            logger.error(f"ML model prediction failed: {str(e)}")
            raise
    
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
    
    def get_current_traffic(self, current_time: str) -> float:
        """
        Get current traffic from realistic traffic pattern
        
        Args:
            current_time: Current timestamp
            
        Returns:
            Current request rate (requests per minute)
        """
        current_ts = pd.Timestamp(current_time)
        hour = current_ts.hour
        minute = current_ts.minute
        dayofweek = current_ts.dayofweek
        
        # Realistic traffic patterns based on business hours
        # Base load: 50-150 requests/min depending on time of day
        if 9 <= hour <= 17:  # Business hours
            base_load = 120 + 30 * np.sin(np.pi * (hour - 9) / 8)  # Peak around noon
        elif 6 <= hour <= 22:  # Extended hours
            base_load = 80 + 20 * np.sin(np.pi * (hour - 6) / 16)
        else:  # Night hours
            base_load = 30 + 10 * np.sin(np.pi * hour / 12)
        
        # Weekend reduction
        if dayofweek >= 5:  # Weekend
            base_load *= 0.6
        
        # Add some randomness and minute-level variation
        minute_variation = 5 * np.sin(np.pi * minute / 30)  # Small variation within hour
        noise = np.random.normal(0, base_load * 0.1)  # 10% noise
        
        result = base_load + minute_variation + noise
        return max(20, min(400, result))  # Bound between 20-400 requests/min
    
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
            
            # Update recent history with current traffic
            current_traffic = self.get_current_traffic(current_time)
            self._update_recent_history(current_traffic)
            
            # Use recent history for lag features if not provided
            if lag_data is None and self.recent_history:
                lag_data = self.recent_history[-10:]  # Use last 10 data points
            
            for interval in intervals:
                # Calculate future timestamp
                future_ts = current_ts + timedelta(minutes=interval)
                
                # Create features for the FUTURE timestamp
                features = self._create_features(future_ts, lag_data)
                
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
    
    def _update_recent_history(self, traffic_value: float):
        """
        Update recent history for trend analysis
        """
        self.recent_history.append(traffic_value)
        
        # Keep only last 50 values
        if len(self.recent_history) > 50:
            self.recent_history = self.recent_history[-50:]
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            "loaded_models": list(self.models.keys()),
            "features": self.feature_names,
            "intervals_supported": ["1m", "5m", "15m"]
        }