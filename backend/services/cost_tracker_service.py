"""
Cost Tracker Service - Tracks accurate time-weighted costs for autoscaling
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class CostTrackerService:
    """Service for tracking time-weighted costs"""
    
    def __init__(self, cost_per_server_per_hour: float = 0.10):
        """Initialize cost tracker"""
        self.cost_per_server_per_hour = cost_per_server_per_hour
        self.scaling_history: List[Dict] = []
        self.current_servers = 0
        self.current_period_start = datetime.now()
        
    def record_scaling_event(self, new_server_count: int, timestamp: datetime = None):
        """Record a scaling event with timestamp"""
        if timestamp is None:
            timestamp = datetime.now()
            
        # Calculate cost for the previous period
        if self.scaling_history or self.current_servers > 0:
            duration = timestamp - self.current_period_start
            duration_hours = duration.total_seconds() / 3600
            period_cost = self.current_servers * self.cost_per_server_per_hour * duration_hours
            
            # Record the completed period
            self.scaling_history.append({
                'start_time': self.current_period_start,
                'end_time': timestamp,
                'servers': self.current_servers,
                'duration_hours': duration_hours,
                'period_cost': period_cost
            })
            
            logger.info(f"Recorded scaling period: {self.current_servers} servers for {duration_hours:.2f}h = ${period_cost:.4f}")
        
        # Start new period
        self.current_servers = new_server_count
        self.current_period_start = timestamp
        
    def get_hourly_cost(self, start_time: datetime, end_time: datetime = None) -> float:
        """Calculate total cost for a specific time period"""
        if end_time is None:
            end_time = datetime.now()
            
        total_cost = 0.0
        
        for period in self.scaling_history:
            # Check if period overlaps with requested time range
            period_start = max(period['start_time'], start_time)
            period_end = min(period['end_time'], end_time)
            
            if period_start < period_end:
                # Calculate overlapping duration
                overlap_duration = period_end - period_start
                overlap_hours = overlap_duration.total_seconds() / 3600
                overlap_cost = period['servers'] * self.cost_per_server_per_hour * overlap_hours
                total_cost += overlap_cost
        
        # Add current ongoing period if it overlaps
        if self.current_period_start < end_time:
            current_start = max(self.current_period_start, start_time)
            current_end = end_time
            
            if current_start < current_end:
                current_duration = current_end - current_start
                current_hours = current_duration.total_seconds() / 3600
                current_cost = self.current_servers * self.cost_per_server_per_hour * current_hours
                total_cost += current_cost
        
        return round(total_cost, 4)
    
    def get_current_hourly_rate(self) -> float:
        """Get current cost rate per hour"""
        return self.current_servers * self.cost_per_server_per_hour
    
    def get_cost_summary(self, hours_back: int = 24) -> Dict:
        """Get cost summary for the last N hours"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        total_cost = self.get_hourly_cost(start_time, end_time)
        
        # Calculate average servers weighted by time
        total_server_hours = 0
        total_hours = 0
        
        for period in self.scaling_history:
            if period['end_time'] > start_time:
                period_start = max(period['start_time'], start_time)
                period_end = min(period['end_time'], end_time)
                
                if period_start < period_end:
                    duration_hours = (period_end - period_start).total_seconds() / 3600
                    total_server_hours += period['servers'] * duration_hours
                    total_hours += duration_hours
        
        # Add current period
        if self.current_period_start < end_time:
            current_start = max(self.current_period_start, start_time)
            current_duration = (end_time - current_start).total_seconds() / 3600
            total_server_hours += self.current_servers * current_duration
            total_hours += current_duration
        
        average_servers = total_server_hours / total_hours if total_hours > 0 else 0
        
        return {
            'total_cost': total_cost,
            'time_period_hours': hours_back,
            'average_servers': round(average_servers, 2),
            'current_servers': self.current_servers,
            'current_hourly_rate': self.get_current_hourly_rate(),
            'scaling_events_count': len(self.scaling_history)
        }
    
    def get_scaling_history(self) -> List[Dict]:
        """Get full scaling history"""
        return self.scaling_history.copy()
    
    def reset(self):
        """Reset cost tracking"""
        self.scaling_history.clear()
        self.current_servers = 0
        self.current_period_start = datetime.now()
        logger.info("Cost tracker reset")