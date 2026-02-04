/**
 * Chart Manager using Chart.js
 */

import { Chart, registerables } from 'chart.js';
import type { ChartConfiguration } from 'chart.js';
import type { DataPoint, ScalingEvent } from './types';

Chart.register(...registerables);

export class ChartManager {
  private trafficChart: Chart | null = null;
  private serversChart: Chart | null = null;
  private costChart: Chart | null = null;

  private trafficData: { time: string[], actual: number[], predicted: number[] } = {
    time: [],
    actual: [],
    predicted: []
  };

  private serversData: { time: string[], count: number[] } = {
    time: [],
    count: []
  };

  private costData: { time: string[], cost: number[] } = {
    time: [],
    cost: []
  };

  private maxDataPoints = 50;

  /**
   * Initialize all charts
   */
  initCharts(): void {
    this.initTrafficChart();
    this.initServersChart();
    this.initCostChart();
  }

  /**
   * Initialize traffic chart
   */
  private initTrafficChart(): void {
    const ctx = document.getElementById('traffic-chart') as HTMLCanvasElement;
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: this.trafficData.time,
        datasets: [
          {
            label: 'Actual Requests',
            data: this.trafficData.actual,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            tension: 0.3,
            fill: true
          },
          {
            label: 'Predicted Requests',
            data: this.trafficData.predicted,
            borderColor: 'rgb(255, 159, 64)',
            backgroundColor: 'rgba(255, 159, 64, 0.1)',
            borderDash: [5, 5],
            tension: 0.3,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Requests/min'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Time'
            }
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        }
      }
    };

    this.trafficChart = new Chart(ctx, config);
  }

  /**
   * Initialize servers chart
   */
  private initServersChart(): void {
    const ctx = document.getElementById('servers-chart') as HTMLCanvasElement;
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: this.serversData.time,
        datasets: [{
          label: 'Active Servers',
          data: this.serversData.count,
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          stepped: true,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1
            },
            title: {
              display: true,
              text: 'Number of Servers'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Time'
            }
          }
        }
      }
    };

    this.serversChart = new Chart(ctx, config);
  }

  /**
   * Initialize cost chart
   */
  private initCostChart(): void {
    const ctx = document.getElementById('cost-chart') as HTMLCanvasElement;
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: this.costData.time,
        datasets: [{
          label: 'Cost ($/hour)',
          data: this.costData.cost,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Cost ($/hour)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Time'
            }
          }
        }
      }
    };

    this.costChart = new Chart(ctx, config);
  }

  /**
   * Update traffic chart with new data
   */
  updateTrafficChart(timestamp: string, actual: number, predicted?: number): void {
    this.trafficData.time.push(this.formatTime(timestamp));
    this.trafficData.actual.push(actual);
    this.trafficData.predicted.push(predicted || 0);

    // Keep only last N points
    if (this.trafficData.time.length > this.maxDataPoints) {
      this.trafficData.time.shift();
      this.trafficData.actual.shift();
      this.trafficData.predicted.shift();
    }

    if (this.trafficChart) {
      // Update chart data explicitly
      this.trafficChart.data.labels = this.trafficData.time;
      this.trafficChart.data.datasets[0].data = this.trafficData.actual;
      this.trafficChart.data.datasets[1].data = this.trafficData.predicted;
      this.trafficChart.update('none'); // Update without animation for smoother updates
    }
  }

  /**
   * Update servers chart
   */
  updateServersChart(timestamp: string, serverCount: number): void {
    this.serversData.time.push(this.formatTime(timestamp));
    this.serversData.count.push(serverCount);

    if (this.serversData.time.length > this.maxDataPoints) {
      this.serversData.time.shift();
      this.serversData.count.shift();
    }

    if (this.serversChart) {
      this.serversChart.data.labels = this.serversData.time;
      this.serversChart.data.datasets[0].data = this.serversData.count;
      this.serversChart.update('none');
    }
  }

  /**
   * Update cost chart
   */
  updateCostChart(timestamp: string, cost: number): void {
    this.costData.time.push(this.formatTime(timestamp));
    this.costData.cost.push(cost);

    if (this.costData.time.length > this.maxDataPoints) {
      this.costData.time.shift();
      this.costData.cost.shift();
    }

    if (this.costChart) {
      this.costChart.data.labels = this.costData.time;
      this.costChart.data.datasets[0].data = this.costData.cost;
      this.costChart.update('none');
    }
  }

  /**
   * Load historical data into traffic chart
   */
  loadHistoricalData(data: DataPoint[]): void {
    this.trafficData.time = data.map(d => this.formatTime(d.timestamp));
    this.trafficData.actual = data.map(d => d.requests);
    this.trafficData.predicted = new Array(data.length).fill(0);

    // Keep only last N points
    if (this.trafficData.time.length > this.maxDataPoints) {
      const start = this.trafficData.time.length - this.maxDataPoints;
      this.trafficData.time = this.trafficData.time.slice(start);
      this.trafficData.actual = this.trafficData.actual.slice(start);
      this.trafficData.predicted = this.trafficData.predicted.slice(start);
    }

    if (this.trafficChart) {
      this.trafficChart.update();
    }
  }

  /**
   * Format timestamp for display
   */
  private formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('vi-VN', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  }

  /**
   * Clear all chart data
   */
  clearAll(): void {
    this.trafficData = { time: [], actual: [], predicted: [] };
    this.serversData = { time: [], count: [] };
    this.costData = { time: [], cost: [] };

    this.trafficChart?.update();
    this.serversChart?.update();
    this.costChart?.update();
  }
}
