/**
 * Type definitions for the Autoscaling Dashboard
 */

export interface DataPoint {
  timestamp: string;
  requests: number;
  bytes: number;
  errors?: number;
}

export interface PredictionItem {
  interval_minutes: number;
  predicted_requests: number;
  predicted_bytes?: number;
  confidence?: number;
  timestamp: string;
}

export interface ForecastResponse {
  timestamp: string;
  predictions: PredictionItem[];
  status: string;
}

export interface ScalingResponse {
  timestamp: string;
  current_servers: number;
  recommended_servers: number;
  action: string;
  reason: string;
  confidence: number;
  estimated_utilization: number;
  estimated_cost_change: number;
  details?: {
    current_capacity: number;
    required_capacity: number;
    current_utilization: number;
    predicted_utilization: number;
    estimated_utilization: number;
    load_increase: number;
    scaling_thresholds: {
      scale_out: number;
      scale_in: number;
      target: number;
    };
  };
}

export interface HistoricalDataResponse {
  data: DataPoint[];
  interval: string;
  start_time: string;
  end_time: string;
  total_records: number;
}

export interface MetricsSummary {
  total_records: number;
  date_range: {
    start: string;
    end: string;
  };
  intervals_available: string[];
  model_info: {
    loaded_models: string[];
    features: string[];
    intervals_supported: string[];
  };
}

export interface AutoscalingConfig {
  min_servers: number;
  max_servers: number;
  max_requests_per_server: number;
  max_bytes_per_server: number;
  cpu_scale_out_threshold: number;
  cpu_scale_in_threshold: number;
  requests_scale_out_threshold: number;
  requests_scale_in_threshold: number;
  scale_out_consecutive_periods: number;
  scale_in_consecutive_periods: number;
  cooldown_period: number;
  cost_per_server_per_hour: number;
  cost_per_gb_transfer: number;
  target_utilization: number;
  scale_out_threshold: number; // legacy
  scale_in_threshold: number; // legacy
  requests_per_server: number; // legacy
  cooldown_minutes: number; // legacy
  status: string;
  last_update: string;
}

export interface ScalingEvent {
  timestamp: string;
  action: string;
  from_servers: number;
  to_servers: number;
  reason: string;
  utilization: number;
}

export interface CostSummary {
  summary: {
    total_cost: number;
    time_period_hours: number;
    average_servers: number;
    current_servers: number;
    current_hourly_rate: number;
    scaling_events_count: number;
  };
  scaling_history: Array<{
    start_time: string;
    end_time: string;
    servers: number;
    duration_hours: number;
    period_cost: number;
  }>;
  cost_per_server_per_hour: number;
}

export interface DashboardState {
  currentRequests: number;
  predictedRequests: number;
  activeServers: number;
  utilization: number;
  costPerHour: number;
  lastUpdate: string;
  connected: boolean;
}
