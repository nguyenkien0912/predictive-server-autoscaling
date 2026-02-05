/**
 * Main application entry point
 */

import { apiService } from './api';
import { ChartManager } from './charts';
import type { 
  DashboardState, 
  ScalingEvent, 
  PredictionItem,
  AutoscalingConfig,
  CostSummary
} from './types';

class Dashboard {
  private chartManager: ChartManager;
  private state: DashboardState;
  private updateInterval: number | null = null;
  private scalingEvents: ScalingEvent[] = [];
  private config: AutoscalingConfig | null = null;
  private currentInterval: string = '5m';
  private lastScalingTime: Date | null = null;  // Track last scaling action
  private multiIntervalPredictions: PredictionItem[] = [];  // Store multi-interval predictions

  constructor() {
    this.chartManager = new ChartManager();
    this.state = {
      currentRequests: 0,
      predictedRequests: 0,
      activeServers: 1,  // Start with 1 server
      utilization: 0,
      costPerHour: 0.10,  // $0.10/hour for 1 server (matches backend config)
      lastUpdate: new Date().toISOString(),
      connected: false
    };
  }

  /**
   * Initialize dashboard
   */
  async init(): Promise<void> {
    console.log('Initializing dashboard...');
    
    // Initialize charts
    this.chartManager.initCharts();

    // Setup event listeners
    this.setupEventListeners();

    // Check backend connection
    await this.checkConnection();

    // Load initial data
    await this.loadInitialData();

    // Start periodic updates
    this.startPeriodicUpdates();

    console.log('Dashboard initialized');
  }

  /**
   * Setup event listeners
   */
  private setupEventListeners(): void {
    // Interval selector
    const intervalSelect = document.getElementById('traffic-interval') as HTMLSelectElement;
    if (intervalSelect) {
      intervalSelect.addEventListener('change', (e) => {
        this.currentInterval = (e.target as HTMLSelectElement).value;
        this.loadHistoricalData();
      });
    }

    // Refresh predictions button
    const refreshBtn = document.getElementById('refresh-predictions');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.updatePredictions());
    }

    // Clear events button
    const clearEventsBtn = document.getElementById('clear-events');
    if (clearEventsBtn) {
      clearEventsBtn.addEventListener('click', () => this.clearEvents());
    }

    // Note: Time is now updated from backend in updateDashboard() every 5 seconds
  }

  /**
   * Check backend connection
   */
  private async checkConnection(): Promise<void> {
    try {
      const isHealthy = await apiService.healthCheck();
      this.state.connected = isHealthy;
      this.updateConnectionStatus(isHealthy);
      
      if (isHealthy) {
        console.log('Backend connection established');
      } else {
        console.warn('Backend is not healthy');
      }
    } catch (error) {
      console.error('Failed to connect to backend:', error);
      this.state.connected = false;
      this.updateConnectionStatus(false);
    }
  }

  /**
   * Load initial data
   */
  private async loadInitialData(): Promise<void> {
    try {
      // Load autoscaling config
      this.config = await apiService.getAutoscalingConfig();
      this.updateSystemInfo();

      // Load historical data
      await this.loadHistoricalData();

      console.log('Initial data loaded');
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  }

  /**
   * Load historical data
   */
  private async loadHistoricalData(): Promise<void> {
    try {
      const response = await apiService.getHistoricalData(
        undefined,
        undefined,
        this.currentInterval,
        100
      );

      if (response.data.length > 0) {
        this.chartManager.loadHistoricalData(response.data);
        
        // Update stats with latest data
        const latest = response.data[response.data.length - 1];
        this.state.currentRequests = latest.requests;
        this.updateStats();
      } else {
        // Generate dummy current requests if no data
        this.state.currentRequests = 100 + Math.random() * 50;
        this.updateStats();
      }
    } catch (error) {
      console.error('Failed to load historical data:', error);
    }
  }

  /**
   * Start periodic updates
   */
  private startPeriodicUpdates(): void {
    // Update every 5 seconds
    this.updateInterval = window.setInterval(() => {
      this.updateDashboard();
    }, 5000);

    // Initial update
    this.updateDashboard();
  }

  /**
   * Update dashboard with latest data
   */
  private async updateDashboard(): Promise<void> {
    if (!this.state.connected) {
      await this.checkConnection();
      if (!this.state.connected) return;
    }

    const startTime = performance.now();
    try {
      // Get current traffic from backend (which has correct NASA 1995 timestamp)
      const trafficData = await apiService.getCurrentTraffic();
      this.state.currentRequests = trafficData.current_requests;
      
      // Use the SAME timestamp from backend for predictions (to avoid timezone mismatch)
      const currentTime = trafficData.timestamp;

      // Update NASA time display in header
      const nasaTime = new Date(currentTime);
      const timeDisplay = document.getElementById('current-time');
      if (timeDisplay) {
        timeDisplay.textContent = `NASA: ${nasaTime.toLocaleTimeString('vi-VN')}`;
      }

      // Log update for visibility
      console.log(`🔄 [${new Date().toLocaleTimeString()}] Dashboard update started - Current: ${Math.round(this.state.currentRequests)} req/min`);

      // Get predictions from backend (using SAME 1995 timestamp)
      const forecast = await apiService.getForecast(currentTime, [1, 5, 15]);
      
      // Update predictions display
      this.updatePredictionsDisplay(forecast.predictions);

      // Use 5-minute prediction from model (not simulated)
      const prediction5m = forecast.predictions.find(p => p.interval_minutes === 5);
      if (prediction5m) {
        this.state.predictedRequests = prediction5m.predicted_requests;
        console.log(`📊 Predicted (5min): ${Math.round(this.state.predictedRequests)} req/min`);
      }

      // Get scaling recommendation
      if (this.state.currentRequests > 0 && this.state.predictedRequests > 0) {
        const scaling = await apiService.getScalingRecommendation(
          this.state.activeServers,
          this.state.currentRequests,
          this.state.predictedRequests,
          this.state.utilization
        );

        // Apply scaling recommendation
        this.applyScalingRecommendation(scaling);
      }

      // Update charts
      this.chartManager.updateTrafficChart(
        currentTime,
        this.state.currentRequests,
        this.state.predictedRequests
      );
      this.chartManager.updateServersChart(currentTime, this.state.activeServers);
      this.chartManager.updateCostChart(currentTime, this.state.costPerHour);

      // Update predictions display (using existing method)
      if (this.multiIntervalPredictions.length > 0) {
        this.updatePredictionsDisplay(this.multiIntervalPredictions);
      }

      // Update cost with time-weighted calculation
      await this.updateAccurateCost();

      // Update stats display
      this.updateStats();
      this.state.lastUpdate = currentTime;

      // Update last updated indicator
      const lastUpdateEl = document.getElementById('last-update');
      if (lastUpdateEl) {
        const now = new Date();
        lastUpdateEl.textContent = `Updated: ${now.toLocaleTimeString()}`;
        lastUpdateEl.classList.add('pulse');
        setTimeout(() => lastUpdateEl.classList.remove('pulse'), 500);
      }

      // Log performance
      const duration = performance.now() - startTime;
      console.log(`✅ Update completed in ${Math.round(duration)}ms`);

    } catch (error) {
      console.error('Dashboard update failed:', error);
      const duration = performance.now() - startTime;
      console.log(`❌ Update failed after ${Math.round(duration)}ms`);
    }
  }

  /**
   * Apply scaling recommendation
   */
  private applyScalingRecommendation(scaling: any): void {
    const oldServers = this.state.activeServers;
    const newServers = scaling.recommended_servers;

    if (oldServers !== newServers) {
      // Check cooldown period (2 minutes = 120000ms)
      const cooldownMs = 120000; // 2 minutes
      const now = new Date();
      
      if (this.lastScalingTime) {
        const timeSinceLastScaling = now.getTime() - this.lastScalingTime.getTime();
        if (timeSinceLastScaling < cooldownMs) {
          const remainingSeconds = Math.ceil((cooldownMs - timeSinceLastScaling) / 1000);
          console.log(`Cooldown active: ${remainingSeconds}s remaining`);
          return; // Skip scaling during cooldown
        }
      }

      // Record scaling event
      this.scalingEvents.push({
        timestamp: scaling.timestamp,
        action: scaling.action,
        from_servers: oldServers,
        to_servers: newServers,
        reason: scaling.reason,
        utilization: scaling.estimated_utilization
      });

      // Update state
      this.state.activeServers = newServers;
      this.lastScalingTime = now; // Update last scaling time
      
      // Update events log
      this.updateEventsLog();
    }

    // Update utilization (cost will be updated by updateAccurateCost method)
    this.state.utilization = scaling.estimated_utilization;
  }

  /**
   * Update predictions display
   */
  private async updatePredictions(): Promise<void> {
    try {
      // Get current traffic to get correct timestamp
      const trafficData = await apiService.getCurrentTraffic();
      const currentTime = trafficData.timestamp;
      
      const forecast = await apiService.getForecast(currentTime, [1, 5, 15]);
      this.updatePredictionsDisplay(forecast.predictions);
    } catch (error) {
      console.error('Failed to update predictions:', error);
    }
  }

  /**
   * Update predictions display
   */
  private updatePredictionsDisplay(predictions: PredictionItem[]): void {
    const container = document.getElementById('predictions-list');
    if (!container) return;

    container.innerHTML = predictions.map(pred => `
      <div class="prediction-item">
        <div class="prediction-header">
          <span class="interval">${pred.interval_minutes} minute${pred.interval_minutes > 1 ? 's' : ''}</span>
          <span class="confidence">${Math.round((pred.confidence || 0) * 100)}% confident</span>
        </div>
        <div class="prediction-value">
          ${Math.round(pred.predicted_requests)} requests/min
        </div>
        <div class="prediction-time">at ${new Date(pred.timestamp).toLocaleTimeString()}</div>
      </div>
    `).join('');

    // Store predictions for dashboard updates
    this.multiIntervalPredictions = predictions;
  }

  /**
   * Update events log
   */
  private updateEventsLog(): void {
    const container = document.getElementById('events-log');
    if (!container) return;

    if (this.scalingEvents.length === 0) {
      container.innerHTML = '<div class="no-events">No scaling events yet</div>';
      return;
    }

    // Show latest 10 events
    const recentEvents = this.scalingEvents.slice(-10).reverse();

    container.innerHTML = recentEvents.map(event => {
      const actionClass = event.action.includes('out') ? 'scale-out' : 
                         event.action.includes('in') ? 'scale-in' : 'maintain';
      const actionIcon = event.action.includes('out') ? '📈' : 
                        event.action.includes('in') ? '📉' : '➡️';

      return `
        <div class="event-item ${actionClass}">
          <div class="event-icon">${actionIcon}</div>
          <div class="event-content">
            <div class="event-header">
              <span class="event-action">${event.action.toUpperCase()}</span>
              <span class="event-time">${new Date(event.timestamp).toLocaleTimeString('vi-VN')}</span>
            </div>
            <div class="event-details">
              ${event.from_servers} → ${event.to_servers} servers
            </div>
            <div class="event-reason">${event.reason}</div>
          </div>
        </div>
      `;
    }).join('');
  }

  /**
   * Clear scaling events
   */
  private clearEvents(): void {
    this.scalingEvents = [];
    this.updateEventsLog();
  }

  /**
   * Update stats display
   */
  private updateStats(): void {
    // Current requests (per minute)
    this.setElementText('current-requests', Math.round(this.state.currentRequests).toString());
    
    // Predicted requests (per minute)  
    this.setElementText('predicted-requests', Math.round(this.state.predictedRequests).toString());
    
    // Active servers
    this.setElementText('active-servers', this.state.activeServers.toString());
    
    // Utilization
    this.setElementText('utilization', `${this.state.utilization.toFixed(1)}%`);
    const utilizationBar = document.getElementById('utilization-bar');
    if (utilizationBar) {
      utilizationBar.style.width = `${Math.min(100, this.state.utilization)}%`;
      
      // Color based on utilization (khớp với backend thresholds)
      if (this.state.utilization > 85) {  // Scale-out threshold
        utilizationBar.style.backgroundColor = '#ef4444';
      } else if (this.state.utilization > 70) {
        utilizationBar.style.backgroundColor = '#f59e0b';
      } else if (this.state.utilization <= 30) {  // Scale-in threshold (30%)
        utilizationBar.style.backgroundColor = '#06b6d4';  // Cyan for low utilization
      } else {
        utilizationBar.style.backgroundColor = '#10b981';  // Green for normal
      }
    }
    
    // Cost per hour - will be updated by updateAccurateCost method
    // (keeping this comment for fallback if API fails)
  }

  /**
   * Update system info
   */
  private updateSystemInfo(): void {
    if (!this.config) return;

    this.setElementText('info-min-servers', this.config.min_servers.toString());
    this.setElementText('info-max-servers', this.config.max_servers.toString());
    this.setElementText('info-scale-out', `${this.config.requests_scale_out_threshold * 100}%`);
    this.setElementText('info-scale-in', `${this.config.requests_scale_in_threshold * 100}%`);
    this.setElementText('info-target', `${this.config.target_utilization}%`);
    this.setElementText('info-capacity', this.config.requests_per_server.toString());
  }

  /**
   * Update connection status
   */
  private updateConnectionStatus(connected: boolean): void {
    const statusBadge = document.getElementById('connection-status');
    if (statusBadge) {
      statusBadge.textContent = connected ? 'Connected' : 'Disconnected';
      statusBadge.className = `status-badge ${connected ? 'connected' : 'disconnected'}`;
    }
  }

  /**
   * Update accurate cost using time-weighted calculation from backend
   */
  private async updateAccurateCost(): Promise<void> {
    try {
      const costSummary: CostSummary = await apiService.getCostSummary(1); // Last 1 hour
      
      // Update cost display with accurate calculation
      this.state.costPerHour = costSummary.summary.current_hourly_rate;
      
      // Update chart with current rate
      this.chartManager.updateCostChart(
        new Date().toISOString(), 
        costSummary.summary.current_hourly_rate
      );

      // Update cost display with more detail
      this.setElementText('cost-hour', `$${costSummary.summary.current_hourly_rate.toFixed(2)}`);
      
      // Show additional cost insights if available
      const costDetails = document.getElementById('cost-details');
      if (costDetails) {
        costDetails.innerHTML = `
          <small>
            Last hour: $${costSummary.summary.total_cost.toFixed(4)} 
            (Avg: ${costSummary.summary.average_servers.toFixed(1)} servers, 
            ${costSummary.summary.scaling_events_count} events)
          </small>
        `;
      }
      
    } catch (error) {
      console.error('Failed to update accurate cost:', error);
      // Fallback to simple calculation
      const fallbackCost = this.state.activeServers * (this.config?.cost_per_server_per_hour || 0.10);
      this.state.costPerHour = fallbackCost;
      this.setElementText('cost-hour', `$${fallbackCost.toFixed(2)}`);
    }
  }

  /**
   * Update current time display
   */
  /**
   * Helper to set element text
   */
  private setElementText(id: string, text: string): void {
    const element = document.getElementById(id);
    if (element) {
      const oldText = element.textContent;
      element.textContent = text;
      
      // Add visual feedback if value changed
      if (oldText !== text && element.classList.contains('stat-value')) {
        element.classList.add('updated');
        setTimeout(() => element.classList.remove('updated'), 300);
      }
    }
  }

  /**
   * Cleanup
   */
  destroy(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
  }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const dashboard = new Dashboard();
  dashboard.init().catch(error => {
    console.error('Failed to initialize dashboard:', error);
  });
});
