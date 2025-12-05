import asyncio
import contextlib
import json
from datetime import datetime
from typing import Dict, Optional, Set

import redis.asyncio as redis
from fastapi import WebSocket

from ..core.config import settings


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriber_groups: Dict[str, Set[str]] = {}
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.pubsub: Optional[redis.client.PubSub] = None
        self.listener_task: Optional[asyncio.Task] = None
        
    async def startup(self):
        """Start the WebSocket manager"""
        try:
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.psubscribe("match:*", "agent:*", "leaderboard")
            self.listener_task = asyncio.create_task(self._listen())
        except Exception:
            # Redis unavailable; continue with in-process broadcasts only
            self.pubsub = None
            self.listener_task = None
        
    async def shutdown(self):
        """Shutdown the WebSocket manager"""
        if self.listener_task:
            self.listener_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.listener_task
        if self.pubsub:
            await self.pubsub.close()
        await self.redis_client.close()
        
    def is_connected(self) -> bool:
        """Check if WebSocket manager is connected"""
        return True
    
    async def _listen(self):
        """Listen for Redis pub/sub messages and fan out to subscribers"""
        while True:
            try:
                if not self.pubsub:
                    await asyncio.sleep(0.1)
                    continue
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("data"):
                    channel = message["channel"]
                    payload = json.loads(message["data"])
                    await self.broadcast_to_channel(channel, payload)
                await asyncio.sleep(0)
            except asyncio.CancelledError:
                break
            except Exception:
                # Avoid crashing the listener; can be enhanced with logging
                await asyncio.sleep(0.5)
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a WebSocket client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
    async def broadcast(self, message: str, channel: str = "general"):
        """Broadcast message to all connected clients"""
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.disconnect(client_id)
                
    async def send_to_client(self, client_id: str, message: dict):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except:
                self.disconnect(client_id)
                
    async def subscribe_to_channel(self, client_id: str, channel: str):
        """Subscribe client to a specific channel"""
        if channel not in self.subscriber_groups:
            self.subscriber_groups[channel] = set()
        self.subscriber_groups[channel].add(client_id)
        
    async def unsubscribe_from_channel(self, client_id: str, channel: str):
        """Unsubscribe client from a specific channel"""
        if channel in self.subscriber_groups:
            self.subscriber_groups[channel].discard(client_id)
            
    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast message to specific channel"""
        if channel in self.subscriber_groups:
            for client_id in self.subscriber_groups[channel]:
                await self.send_to_client(client_id, message)
                
    async def publish_match_update(self, match_id: int, data: dict):
        """Publish match update to Redis and WebSocket"""
        channel = f"match:{match_id}"
        message = {
            "type": "match_update",
            "match_id": match_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to Redis
        await self.redis_client.publish(channel, json.dumps(message))
        
        # Broadcast to WebSocket subscribers
        await self.broadcast_to_channel(channel, message)
        
    async def publish_agent_update(self, agent_id: int, data: dict):
        """Publish agent update"""
        channel = f"agent:{agent_id}"
        message = {
            "type": "agent_update",
            "agent_id": agent_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.publish(channel, json.dumps(message))
        await self.broadcast_to_channel(channel, message)


    async def publish_leaderboard_update(self, data: dict):
        """Publish leaderboard update"""
        channel = "leaderboard"
        message = {
            "type": "leaderboard_update",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.publish(channel, json.dumps(message))
        await self.broadcast_to_channel(channel, message)


# Shared instance for app-wide usage
ws_manager = WebSocketManager()