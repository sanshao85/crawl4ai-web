/**
 * WebSocket Manager for Crawl4AI Web Application
 */

class WebSocketManager {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.taskSubscriptions = new Set();
        
        // Event handlers
        this.onStatusChange = null;
        this.onTaskUpdate = null;
        this.onTaskCompleted = null;
        this.onTaskError = null;
        this.onMessage = null;
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = (event) => {
                console.log('WebSocket connected');
                this.connected = true;
                this.reconnectAttempts = 0;
                
                if (this.onStatusChange) {
                    this.onStatusChange(true);
                }
                
                // Resubscribe to tasks
                this.resubscribeToTasks();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('WebSocket disconnected');
                this.connected = false;
                
                if (this.onStatusChange) {
                    this.onStatusChange(false);
                }
                
                // Attempt to reconnect
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            this.attemptReconnect();
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.connected = false;
        this.taskSubscriptions.clear();
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, delay);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }
    
    send(message) {
        if (this.connected && this.ws) {
            try {
                this.ws.send(JSON.stringify(message));
                return true;
            } catch (error) {
                console.error('Error sending WebSocket message:', error);
                return false;
            }
        } else {
            console.warn('WebSocket not connected, cannot send message');
            return false;
        }
    }
    
    ping() {
        return this.send({
            type: 'ping',
            data: {},
            timestamp: new Date().toISOString()
        });
    }
    
    subscribeToTask(taskId) {
        this.taskSubscriptions.add(taskId);
        return this.send({
            type: 'subscribe_task',
            data: { task_id: taskId },
            timestamp: new Date().toISOString()
        });
    }
    
    unsubscribeFromTask(taskId) {
        this.taskSubscriptions.delete(taskId);
        return this.send({
            type: 'unsubscribe_task',
            data: { task_id: taskId },
            timestamp: new Date().toISOString()
        });
    }
    
    getTaskStatus(taskId) {
        return this.send({
            type: 'get_status',
            data: { task_id: taskId },
            timestamp: new Date().toISOString()
        });
    }
    
    resubscribeToTasks() {
        for (const taskId of this.taskSubscriptions) {
            this.subscribeToTask(taskId);
        }
    }
    
    handleMessage(message) {
        const { type, data } = message;
        
        switch (type) {
            case 'pong':
                console.log('Received pong from server');
                break;
                
            case 'subscribed':
                console.log(`Subscribed to task: ${data.task_id}`);
                break;
                
            case 'unsubscribed':
                console.log(`Unsubscribed from task: ${data.task_id}`);
                break;
                
            case 'task_update':
                if (this.onTaskUpdate) {
                    this.onTaskUpdate(data);
                }
                break;
                
            case 'task_completed':
                if (this.onTaskCompleted) {
                    this.onTaskCompleted(data);
                }
                break;
                
            case 'task_error':
                if (this.onTaskError) {
                    this.onTaskError(data);
                }
                break;
                
            case 'task_status':
                if (this.onTaskUpdate) {
                    this.onTaskUpdate(data);
                }
                break;
                
            case 'error':
                console.error('WebSocket error:', data.message);
                break;
                
            default:
                console.log('Unknown message type:', type);
                if (this.onMessage) {
                    this.onMessage(message);
                }
        }
    }
}

// Utility functions for WebSocket management
window.WebSocketManager = WebSocketManager;

// Auto-ping to keep connection alive
setInterval(() => {
    if (window.wsManager && window.wsManager.connected) {
        window.wsManager.ping();
    }
}, 30000); // Ping every 30 seconds
