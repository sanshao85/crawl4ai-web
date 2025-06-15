"""
WebSocket API for real-time communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
import asyncio
from datetime import datetime

from app.models.response import WebSocketMessage
from app.services.crawler_service import get_crawler_service

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.task_subscribers: Dict[str, set] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove from all task subscriptions
        for task_id in list(self.task_subscribers.keys()):
            if client_id in self.task_subscribers[task_id]:
                self.task_subscribers[task_id].remove(client_id)
                if not self.task_subscribers[task_id]:
                    del self.task_subscribers[task_id]
        
        print(f"Client {client_id} disconnected")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_task_subscribers(self, message: dict, task_id: str):
        """Broadcast a message to all clients subscribed to a task."""
        if task_id in self.task_subscribers:
            disconnected_clients = []
            for client_id in self.task_subscribers[task_id]:
                try:
                    await self.send_personal_message(message, client_id)
                except Exception:
                    disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                self.task_subscribers[task_id].discard(client_id)
    
    def subscribe_to_task(self, client_id: str, task_id: str):
        """Subscribe a client to task updates."""
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        self.task_subscribers[task_id].add(client_id)
    
    def unsubscribe_from_task(self, client_id: str, task_id: str):
        """Unsubscribe a client from task updates."""
        if task_id in self.task_subscribers:
            self.task_subscribers[task_id].discard(client_id)
            if not self.task_subscribers[task_id]:
                del self.task_subscribers[task_id]


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    
    Supports the following message types:
    - ping: Health check
    - subscribe_task: Subscribe to task updates
    - unsubscribe_task: Unsubscribe from task updates
    - get_status: Get current task status
    """
    
    # Generate client ID (in production, you might want to use authentication)
    client_id = f"client_{datetime.now().timestamp()}"
    
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                message_data = message.get("data", {})
                
                # Handle different message types
                if message_type == "ping":
                    await handle_ping(client_id, message_data)
                
                elif message_type == "subscribe_task":
                    await handle_subscribe_task(client_id, message_data)
                
                elif message_type == "unsubscribe_task":
                    await handle_unsubscribe_task(client_id, message_data)
                
                elif message_type == "get_status":
                    await handle_get_status(client_id, message_data)
                
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "data": {"message": f"Unknown message type: {message_type}"},
                        "timestamp": datetime.now().isoformat()
                    }, client_id)
            
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"},
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            except Exception as e:
                await manager.send_personal_message({
                    "type": "error",
                    "data": {"message": f"Error processing message: {str(e)}"},
                    "timestamp": datetime.now().isoformat()
                }, client_id)
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)


async def handle_ping(client_id: str, data: dict):
    """Handle ping messages."""
    await manager.send_personal_message({
        "type": "pong",
        "data": {"message": "Server is alive"},
        "timestamp": datetime.now().isoformat()
    }, client_id)


async def handle_subscribe_task(client_id: str, data: dict):
    """Handle task subscription requests."""
    task_id = data.get("task_id")
    if not task_id:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "task_id is required"},
            "timestamp": datetime.now().isoformat()
        }, client_id)
        return
    
    manager.subscribe_to_task(client_id, task_id)
    
    await manager.send_personal_message({
        "type": "subscribed",
        "data": {"task_id": task_id, "message": f"Subscribed to task {task_id}"},
        "timestamp": datetime.now().isoformat()
    }, client_id)


async def handle_unsubscribe_task(client_id: str, data: dict):
    """Handle task unsubscription requests."""
    task_id = data.get("task_id")
    if not task_id:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "task_id is required"},
            "timestamp": datetime.now().isoformat()
        }, client_id)
        return
    
    manager.unsubscribe_from_task(client_id, task_id)
    
    await manager.send_personal_message({
        "type": "unsubscribed",
        "data": {"task_id": task_id, "message": f"Unsubscribed from task {task_id}"},
        "timestamp": datetime.now().isoformat()
    }, client_id)


async def handle_get_status(client_id: str, data: dict):
    """Handle status request messages."""
    task_id = data.get("task_id")
    if not task_id:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "task_id is required"},
            "timestamp": datetime.now().isoformat()
        }, client_id)
        return
    
    try:
        crawler_service = get_crawler_service()
        task = await crawler_service.get_task(task_id)
        
        if task:
            await manager.send_personal_message({
                "type": "task_status",
                "data": {
                    "task_id": task_id,
                    "status": task.status,
                    "progress": task.progress,
                    "updated_at": task.updated_at.isoformat()
                },
                "timestamp": datetime.now().isoformat()
            }, client_id)
        else:
            await manager.send_personal_message({
                "type": "error",
                "data": {"message": f"Task {task_id} not found"},
                "timestamp": datetime.now().isoformat()
            }, client_id)
    
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": f"Error getting task status: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }, client_id)


# Function to broadcast task updates (to be called from crawler service)
async def broadcast_task_update(task_id: str, status: str, progress: float, data: dict = None):
    """Broadcast task updates to subscribed clients."""
    message = {
        "type": "task_update",
        "data": {
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "timestamp": datetime.now().isoformat(),
            **(data or {})
        }
    }
    
    await manager.broadcast_to_task_subscribers(message, task_id)


# Function to broadcast task completion
async def broadcast_task_completed(task_id: str, result: dict):
    """Broadcast task completion to subscribed clients."""
    message = {
        "type": "task_completed",
        "data": {
            "task_id": task_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.broadcast_to_task_subscribers(message, task_id)


# Function to broadcast task error
async def broadcast_task_error(task_id: str, error: str):
    """Broadcast task error to subscribed clients."""
    message = {
        "type": "task_error",
        "data": {
            "task_id": task_id,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    await manager.broadcast_to_task_subscribers(message, task_id)
