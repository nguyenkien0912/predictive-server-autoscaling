/**
 * API Service for communicating with backend
 */

import type {
  ForecastResponse,
  ScalingResponse,
  HistoricalDataResponse,
  MetricsSummary,
  AutoscalingConfig,
  CostSummary
} from './types';

// Auto-detect API URL based on environment
// Development (Vite dev server on port 3000): use http://localhost:5000/api
// Production/Docker (served by Nginx on port 80): use relative /api path
const getApiBaseUrl = (): string => {
  // Check if running on development port 3000
  if (window.location.port === '3000') {
    return 'http://localhost:5000/api';
  }
  // Production/Docker - use relative path (Nginx will proxy to backend)
  return '/api';
};

const API_BASE_URL = getApiBaseUrl();

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    console.log(`API Base URL: ${this.baseUrl}`);
  }

  /**
   * Get current traffic from backend
   */
  async getCurrentTraffic(): Promise<{ timestamp: string; current_requests: number }> {
    const response = await fetch(`${this.baseUrl}/current-traffic`);
    if (!response.ok) {
      throw new Error('Failed to get current traffic');
    }
    return response.json();
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      const data = await response.json();
      return data.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  /**
   * Get forecast for specified time
   */
  async getForecast(currentTime: string, intervals: number[] = [1, 5, 15]): Promise<ForecastResponse> {
    const response = await fetch(`${this.baseUrl}/forecast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_time: currentTime,
        intervals: intervals
      })
    });

    if (!response.ok) {
      throw new Error(`Forecast request failed: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Get scaling recommendation
   */
  async getScalingRecommendation(
    currentServers: number,
    currentLoad: number,
    predictedLoad: number,
    currentUtilization?: number
  ): Promise<ScalingResponse> {
    const response = await fetch(`${this.baseUrl}/recommend-scaling`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_servers: currentServers,
        current_load: currentLoad,
        predicted_load: predictedLoad,
        current_utilization: currentUtilization
      })
    });

    if (!response.ok) {
      throw new Error(`Scaling recommendation failed: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Get historical data
   */
  async getHistoricalData(
    startTime?: string,
    endTime?: string,
    interval: string = '5m',
    limit: number = 1000
  ): Promise<HistoricalDataResponse> {
    const params = new URLSearchParams({
      interval: interval,
      limit: limit.toString()
    });

    if (startTime) params.append('start_time', startTime);
    if (endTime) params.append('end_time', endTime);

    const response = await fetch(`${this.baseUrl}/historical-data?${params.toString()}`);

    if (!response.ok) {
      throw new Error(`Historical data request failed: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Get metrics summary
   */
  async getMetricsSummary(): Promise<MetricsSummary> {
    const response = await fetch(`${this.baseUrl}/metrics/summary`);

    if (!response.ok) {
      throw new Error(`Metrics summary request failed: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Get autoscaling configuration
   */
  async getAutoscalingConfig(): Promise<AutoscalingConfig> {
    const response = await fetch(`${this.baseUrl}/autoscaling/config`);

    if (!response.ok) {
      throw new Error(`Config request failed: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Get accurate cost summary with time-weighted calculations
   */
  async getCostSummary(hours: number = 24): Promise<CostSummary> {
    const response = await fetch(`${this.baseUrl}/cost/summary?hours=${hours}`);

    if (!response.ok) {
      throw new Error(`Cost summary request failed: ${response.statusText}`);
    }

    return await response.json();
  }
}

export const apiService = new ApiService();
