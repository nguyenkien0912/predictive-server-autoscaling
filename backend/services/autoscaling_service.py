"""
Autoscaling Service - Provides server scaling recommendations
"""

import numpy as np
from datetime import datetime
from typing import Dict, Optional
import logging

from models.response_models import ScalingResponse
from .cost_tracker_service import CostTrackerService

logger = logging.getLogger(__name__)

class AutoscalingService:
    """Service for autoscaling recommendations"""
    
    def __init__(self):
        """Initialize autoscaling service with configuration"""
        self.config = {
            # ---- THÔNG SỐ MÁY CHỦ ---- (từ Autoscaling_Optimization.ipynb)
            'min_servers': 1,
            'max_servers': 50,
            'max_requests_per_server': 200,  # Số request/phút tối đa 1 server có thể xử lý
            'max_bytes_per_server': 50_000_000,  # 50MB/phút tối đa 1 server
            
            # ---- NGƯỠNG SCALING ---- (từ Autoscaling_Optimization.ipynb)
            'cpu_scale_out_threshold': 70,  # CPU > 70% -> scale out
            'cpu_scale_in_threshold': 30,   # CPU < 30% -> scale in  
            'requests_scale_out_threshold': 0.8,  # > 80% capacity -> scale out
            'requests_scale_in_threshold': 0.4,   # < 40% capacity -> scale in
            
            # ---- CHÍNH SÁCH THỜI GIAN ---- (từ Autoscaling_Optimization.ipynb)
            'scale_out_consecutive_periods': 2,  # Scale-out sau 2 period liên tiếp
            'scale_in_consecutive_periods': 5,   # Scale-in sau 5 period liên tiếp
            'cooldown_period': 2,  # 2 phút cooldown sau mỗi scaling event (đổi từ 5 về 2)
            
            # ---- CHI PHÍ ---- (từ Autoscaling_Optimization.ipynb)
            'cost_per_server_per_hour': 0.10,  # $0.10/server/giờ
            'cost_per_gb_transfer': 0.02,      # $0.02/GB transfer
            
            # Legacy compatibility
            'target_utilization': 70.0,
            'scale_out_threshold': 80.0,  # Changed from 85% to 80%
            'scale_in_threshold': 40.0,   # Changed from 30% to 40%
            'requests_per_server': 200,   # Same as max_requests_per_server
            'cooldown_minutes': 2,        # Changed back from 5 to 2 minutes
        }
        self.last_scaling_time = None
        self.startup_time = datetime.now()  # Track startup time
        self.startup_grace_period = 30  # 30 seconds grace period
        
        # Initialize cost tracker
        self.cost_tracker = CostTrackerService(self.config['cost_per_server_per_hour'])
        self.cost_tracker.record_scaling_event(self.config['min_servers'])  # Start with min servers
    
    def recommend(
        self,
        current_servers: int,
        current_load: float,
        predicted_load: float,
        current_utilization: Optional[float] = None
    ) -> ScalingResponse:
        """
        Generate scaling recommendation
        
        Args:
            current_servers: Current number of servers
            current_load: Current request load (requests/min)
            predicted_load: Predicted future load (requests/min)
            current_utilization: Current utilization percentage
            
        Returns:
            ScalingResponse with recommendation
        """
        logger.info(f"Generating recommendation: servers={current_servers}, load={current_load:.2f}, predicted={predicted_load:.2f}")
        
        # Check startup grace period
        if (datetime.now() - self.startup_time).total_seconds() < self.startup_grace_period:
            cost_summary = self.cost_tracker.get_cost_summary(hours_back=1)
            return ScalingResponse(
                timestamp=datetime.now().isoformat(),
                current_servers=current_servers,
                recommended_servers=current_servers,
                action='startup-grace',
                reason=f'Startup grace period active ({self.startup_grace_period}s)',
                confidence=1.0,
                estimated_utilization=0,
                estimated_cost_change=0,
                details={
                    'startup_grace_remaining': self.startup_grace_period - (datetime.now() - self.startup_time).total_seconds(),
                    'accurate_cost_tracking': {
                        'current_hourly_rate': cost_summary['current_hourly_rate'],
                        'average_servers_last_hour': cost_summary['average_servers'],
                        'total_cost_last_hour': cost_summary['total_cost'],
                        'scaling_events_last_hour': cost_summary['scaling_events_count']
                    }
                }
            )
        
        # Check cooldown period
        if self.last_scaling_time is not None:
            time_since_last_scaling = (datetime.now() - self.last_scaling_time).total_seconds() / 60
            if time_since_last_scaling < self.config['cooldown_minutes']:
                remaining_cooldown = self.config['cooldown_minutes'] - time_since_last_scaling
                cost_summary = self.cost_tracker.get_cost_summary(hours_back=1)
                return ScalingResponse(
                    timestamp=datetime.now().isoformat(),
                    current_servers=current_servers,
                    recommended_servers=current_servers,
                    action='cooldown',
                    reason=f'Cooldown period active (remaining: {remaining_cooldown:.1f}m)',
                    confidence=1.0,
                    estimated_utilization=current_utilization or 0,
                    estimated_cost_change=0,
                    details={
                        'cooldown_remaining_minutes': remaining_cooldown,
                        'accurate_cost_tracking': {
                            'current_hourly_rate': cost_summary['current_hourly_rate'],
                            'average_servers_last_hour': cost_summary['average_servers'],
                            'total_cost_last_hour': cost_summary['total_cost'],
                            'scaling_events_last_hour': cost_summary['scaling_events_count']
                        }
                    }
                )
        
        # Calculate current utilization if not provided
        if current_utilization is None:
            max_capacity = current_servers * self.config['requests_per_server']
            current_utilization = (current_load / max_capacity * 100) if max_capacity > 0 else 0
        
        # Calculate predicted utilization with current servers
        max_capacity = current_servers * self.config['requests_per_server']
        predicted_utilization = (predicted_load / max_capacity * 100) if max_capacity > 0 else 0
        
        # Determine required servers for predicted load
        required_servers = self._calculate_required_servers(predicted_load)
        
        # Apply scaling logic
        action, recommended_servers, reason, confidence = self._decide_scaling_action(
            current_servers=current_servers,
            required_servers=required_servers,
            current_utilization=current_utilization,
            predicted_utilization=predicted_utilization,
            predicted_load=predicted_load
        )
        
        # Calculate metrics
        estimated_utilization = self._calculate_estimated_utilization(
            predicted_load, recommended_servers
        )
        
        estimated_cost_change = self._calculate_cost_change(
            current_servers, recommended_servers
        )
        
        # Create detailed response
        details = {
            'current_capacity': current_servers * self.config['requests_per_server'],
            'required_capacity': required_servers * self.config['requests_per_server'],
            'current_utilization': round(current_utilization, 2),
            'predicted_utilization': round(predicted_utilization, 2),
            'estimated_utilization': round(estimated_utilization, 2),
            'load_increase': round((predicted_load - current_load) / current_load * 100, 2) if current_load > 0 else 0,
            'scaling_thresholds': {
                'scale_out': self.config['scale_out_threshold'],
                'scale_in': self.config['scale_in_threshold'],
                'target': self.config['target_utilization']
            }
        }
        
        # Update last_scaling_time nếu có scaling action thực sự
        if action in ['scale-out', 'scale-in'] and recommended_servers != current_servers:
            self.last_scaling_time = datetime.now()
            # Record scaling event for accurate cost tracking
            self.cost_tracker.record_scaling_event(recommended_servers)
            logger.info(f"Scaling action executed: {action}, servers: {current_servers} -> {recommended_servers}")
        
        # Get accurate cost information
        cost_summary = self.cost_tracker.get_cost_summary(hours_back=1)
        
        return ScalingResponse(
            timestamp=datetime.now().isoformat(),
            current_servers=current_servers,
            recommended_servers=recommended_servers,
            action=action,
            reason=reason,
            confidence=confidence,
            estimated_utilization=estimated_utilization,
            estimated_cost_change=estimated_cost_change,
            details={
                **details,
                'accurate_cost_tracking': {
                    'current_hourly_rate': cost_summary['current_hourly_rate'],
                    'average_servers_last_hour': cost_summary['average_servers'],
                    'total_cost_last_hour': cost_summary['total_cost'],
                    'scaling_events_last_hour': cost_summary['scaling_events_count']
                }
            }
        )
    
    def _calculate_required_servers(self, predicted_load: float) -> int:
        """
        Calculate number of servers required for predicted load
        Sử dụng logic từ Autoscaling_Optimization.ipynb với 20% buffer
        """
        # Tính số server cần thiết cho requests
        servers_for_requests = np.ceil(predicted_load / self.config['max_requests_per_server'])
        
        # Thêm 20% buffer để đảm bảo hiệu năng (từ notebook)
        required_servers = np.ceil(servers_for_requests * 1.2)
        
        # Apply min/max constraints
        required = max(self.config['min_servers'], min(self.config['max_servers'], int(required_servers)))
        
        return required
    
    def _decide_scaling_action(
        self,
        current_servers: int,
        required_servers: int,
        current_utilization: float,
        predicted_utilization: float,
        predicted_load: float
    ) -> tuple:
        """
        Decide scaling action based on metrics
        
        Returns:
            (action, recommended_servers, reason, confidence)
        """
        # Check if predicted utilization exceeds scale-out threshold (80% từ notebook)
        scale_out_threshold = self.config['requests_scale_out_threshold'] * 100  # Convert 0.8 -> 80%
        if predicted_utilization > scale_out_threshold:
            # Scale out by adding only 1 server at a time for smooth scaling
            recommended = current_servers + 1
            recommended = min(recommended, self.config['max_servers'])
            
            return (
                'scale-out',
                recommended,
                f'Predicted utilization ({predicted_utilization:.1f}%) exceeds threshold ({scale_out_threshold}%)',
                0.9
            )
        
        # Check if predicted utilization is below scale-in threshold (40% từ notebook)
        scale_in_threshold = self.config['requests_scale_in_threshold'] * 100  # Convert 0.4 -> 40%
        if predicted_utilization < scale_in_threshold:
            # Scale in by removing only 1 server at a time for smooth scaling
            recommended = current_servers - 1
            recommended = max(recommended, self.config['min_servers'])
            
            # Only scale in if we can save at least 1 server
            if recommended >= self.config['min_servers'] and recommended < current_servers:
                return (
                    'scale-in',
                    recommended,
                    f'Predicted utilization ({predicted_utilization:.1f}%) below threshold ({scale_in_threshold}%)',
                    0.8
                )
            else:
                return (
                    'maintain',
                    current_servers,
                    f'Already at minimum servers (min={self.config["min_servers"]})',
                    0.7
                )
        
        # Utilization is within acceptable range
        else:
            # Check if small adjustment is needed
            if abs(required_servers - current_servers) > 1:
                return (
                    'adjust',
                    required_servers,
                    f'Adjusting to maintain target utilization ({self.config["target_utilization"]}%)',
                    0.75
                )
            else:
                return (
                    'maintain',
                    current_servers,
                    f'Current capacity is adequate for predicted load',
                    0.85
                )
    
    def _calculate_estimated_utilization(
        self,
        predicted_load: float,
        servers: int
    ) -> float:
        """Calculate estimated utilization with given number of servers"""
        max_capacity = servers * self.config['requests_per_server']
        utilization = (predicted_load / max_capacity * 100) if max_capacity > 0 else 0
        return round(utilization, 2)
    
    def _calculate_cost_change(
        self,
        current_servers: int,
        recommended_servers: int
    ) -> float:
        """Calculate estimated cost change per hour"""
        server_diff = recommended_servers - current_servers
        cost_change = server_diff * self.config['cost_per_server_per_hour']
        return round(cost_change, 2)
    
    def get_config(self) -> Dict:
        """Get current autoscaling configuration"""
        return {
            **self.config,
            'status': 'active',
            'last_update': datetime.now().isoformat()
        }
    
    def update_config(self, new_config: Dict):
        """Update autoscaling configuration"""
        self.config.update(new_config)
        logger.info(f"Updated autoscaling config: {new_config}")
