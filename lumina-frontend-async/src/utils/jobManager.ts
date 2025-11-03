import { JobStatus, JobUpdate } from '../types';
// write a line to import API_BASE_URL from './api';
import { API_BASE_URL } from './api';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';


export interface JobManagerOptions {
  onUpdate?: (update: JobUpdate) => void;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
  pollInterval?: number; // Fallback polling interval in ms
}

/**
 * WebSocket-based Job Manager
 * Connects to backend job status WebSocket and tracks progress
 */
export class JobManager {
  private ws: WebSocket | null = null;
  private isComplete = false;
  private jobId: string;
  private options: JobManagerOptions;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private pollTimer: NodeJS.Timeout | null = null;

  constructor(jobId: string, options: JobManagerOptions = {}) {
    this.jobId = jobId;
    this.options = {
      pollInterval: 2000, // Poll every 2 seconds as fallback
      ...options,
    };
  }

  /**
   * Start tracking the job
   */
  async start(): Promise<any> {
    return new Promise((resolve, reject) => {
      // Try WebSocket first
      this.connectWebSocket(resolve, reject);

      // Set a timeout - if WebSocket doesn't connect in 5 seconds, fall back to polling
      setTimeout(() => {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
          console.warn('WebSocket connection timeout, falling back to polling');
          this.startPolling(resolve, reject);
        }
      }, 5000);
    });
  }

  /**
   * Connect via WebSocket
   */
  private connectWebSocket(resolve: (value: any) => void, reject: (reason: any) => void) {
    try {
      const wsUrl = `${WS_BASE_URL}/ws/status/${this.jobId}`;
      console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log(`✅ WebSocket connected for job ${this.jobId}`);
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const update: JobUpdate = JSON.parse(event.data);
          console.log(`📨 Job update:`, update);

          // Call update callback
          this.options.onUpdate?.(update);

          // Check if job is complete
          if (update.status === 'COMPLETED') {
            this.isComplete = true;
            this.options.onComplete?.(update.result);
            this.cleanup();
            resolve(update.result);
          } else if (update.status === 'FAILED') {
            this.isComplete = true;
            this.options.onError?.(update.message);
            this.cleanup();
            reject(new Error(update.message));
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Don't reject immediately - we'll try polling
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        // Try to reconnect or fall back to polling
        if (!this.isComplete && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`Reconnect attempt ${this.reconnectAttempts}...`);
          setTimeout(() => this.connectWebSocket(resolve, reject), 2000);
        } else {
          console.warn('Max reconnection attempts reached, falling back to polling');
          this.startPolling(resolve, reject);
        }
      };
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.startPolling(resolve, reject);
    }
  }

  /**
   * Fallback: Poll job status via HTTP
   */
  private async startPolling(resolve: (value: any) => void, reject: (reason: any) => void) {
    console.log(`🔄 Starting polling for job ${this.jobId}`);

    const poll = async () => {
      try {
        // const response = await fetch(`http://localhost:8000/jobs/${this.jobId}/status`);
        const response = await fetch(`${API_BASE_URL}/jobs/${this.jobId}/status`);
        const update: JobUpdate = await response.json();

        console.log(`📊 Poll update:`, update);

        // Call update callback
        this.options.onUpdate?.(update);

        // Check if job is complete
        if (update.status === 'COMPLETED') {
          this.isComplete = true;
          this.options.onComplete?.(update.result);
          this.cleanup();
          resolve(update.result);
        } else if (update.status === 'FAILED') {
          this.isComplete = true;
          this.options.onError?.(update.message);
          this.cleanup();
          reject(new Error(update.message));
        } else {
          // Continue polling
          this.pollTimer = setTimeout(poll, this.options.pollInterval);
        }
      } catch (error) {
        console.error('Polling error:', error);
        this.cleanup();
        reject(error);
      }
    };

    poll();
  }

  /**
   * Stop tracking and cleanup
   */
  stop() {
    this.cleanup();
  }

  private cleanup() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.pollTimer) {
      clearTimeout(this.pollTimer);
      this.pollTimer = null;
    }
  }
}

/**
 * Convenience function to track a job and return a promise
 */
export function trackJob(
  jobId: string,
  onUpdate?: (update: JobUpdate) => void
): Promise<any> {
  const manager = new JobManager(jobId, { onUpdate });
  return manager.start();
}