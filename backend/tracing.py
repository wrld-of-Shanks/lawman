"""
SPECTER Legal Assistant - Tracing and Audit System
Tracks all user actions, system events, and changes for monitoring and debugging.
"""

import os
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request, Response
import json

class TracingSystem:
    def __init__(self):
        self.client = None
        self.db = None
        self.traces_collection = None
        
    async def initialize(self):
        """Initialize MongoDB connection for tracing"""
        mongodb_url = os.getenv("MONGODB_URL") or os.getenv("MONGO_URL") or "mongodb://localhost:27017"
        database_name = os.getenv("DATABASE_NAME", "specter_legal")
        
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client[database_name]
        self.traces_collection = self.db.traces
        
        # Create indexes for efficient querying
        await self.traces_collection.create_index([("timestamp", -1)])
        await self.traces_collection.create_index([("event_type", 1)])
        await self.traces_collection.create_index([("user_id", 1)])
        await self.traces_collection.create_index([("session_id", 1)])
        
        print("✅ Tracing system initialized")

    async def log_trace(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log a trace event to MongoDB"""
        if self.traces_collection is None:
            return
            
        # Sanitize sensitive data
        sanitized_data = self._sanitize_data(data.copy())
        
        trace_entry = {
            "timestamp": datetime.now(timezone.utc),
            "event_type": event_type,
            "data": sanitized_data,
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "version": "1.2.0"
        }
        
        try:
            await self.traces_collection.insert_one(trace_entry)
        except Exception as e:
            print(f"❌ Failed to log trace: {e}")

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from trace data"""
        sensitive_fields = [
            'password', 'token', 'access_token', 'refresh_token', 
            'otp', 'secret', 'key', 'authorization'
        ]
        
        for field in sensitive_fields:
            if field in data:
                data[field] = "[REDACTED]"
                
        # Recursively sanitize nested dictionaries
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self._sanitize_data(value)
                
        return data

    async def get_traces(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve traces with optional filtering"""
        if self.traces_collection is None:
            return []
            
        query = {}
        
        if event_type:
            query["event_type"] = event_type
        if user_id:
            query["user_id"] = user_id
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
                
        cursor = self.traces_collection.find(query).sort("timestamp", -1).limit(limit)
        traces = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for trace in traces:
            trace["_id"] = str(trace["_id"])
            
        return traces

    async def get_user_activity(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user activity summary for the last N days"""
        if self.traces_collection is None:
            return {}
            
        start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date.replace(day=start_date.day - days)
        
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                    "last_occurrence": {"$max": "$timestamp"}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        result = await self.traces_collection.aggregate(pipeline).to_list(length=None)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "activity_summary": result,
            "total_events": sum(item["count"] for item in result)
        }

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        if self.traces_collection is None:
            return {}
            
        total_traces = await self.traces_collection.count_documents({})
        
        # Get event type distribution
        pipeline = [
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        event_distribution = await self.traces_collection.aggregate(pipeline).to_list(length=None)
        
        # Get recent activity (last 24 hours)
        last_24h = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        recent_activity = await self.traces_collection.count_documents({
            "timestamp": {"$gte": last_24h}
        })
        
        return {
            "total_traces": total_traces,
            "event_distribution": event_distribution,
            "recent_activity_24h": recent_activity,
            "system_version": "1.2.0"
        }

# Global tracing instance
tracing = TracingSystem()

# Event type constants
class TraceEvents:
    # Authentication events
    AUTH_REGISTER = "auth.register"
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FORGOT_PASSWORD = "auth.forgot_password"
    AUTH_RESET_PASSWORD = "auth.reset_password"
    AUTH_TOKEN_REFRESH = "auth.token_refresh"
    
    # Chat events
    CHAT_REQUEST = "chat.request"
    CHAT_RESPONSE = "chat.response"
    CHAT_ERROR = "chat.error"
    
    # Document events
    DOC_UPLOAD = "document.upload"
    DOC_PROCESS = "document.process"
    DOC_ERROR = "document.error"
    
    # System events
    SYSTEM_START = "system.start"
    SYSTEM_ERROR = "system.error"
    SYSTEM_HEALTH_CHECK = "system.health_check"
    
    # User events
    USER_PROFILE_UPDATE = "user.profile_update"
    USER_SESSION_START = "user.session_start"
    USER_SESSION_END = "user.session_end"

async def log_auth_event(event_type: str, email: str, success: bool, details: Dict[str, Any] = None):
    """Helper function to log authentication events"""
    data = {
        "email": email,
        "success": success,
        "details": details or {}
    }
    await tracing.log_trace(event_type, data, user_id=email)

async def log_chat_event(user_id: str, message: str, response: str = None, error: str = None):
    """Helper function to log chat events"""
    data = {
        "message_length": len(message),
        "message_preview": message[:100] + "..." if len(message) > 100 else message,
        "response_length": len(response) if response else 0,
        "error": error
    }
    event_type = TraceEvents.CHAT_ERROR if error else TraceEvents.CHAT_REQUEST
    await tracing.log_trace(event_type, data, user_id=user_id)

async def log_system_event(event_type: str, details: Dict[str, Any]):
    """Helper function to log system events"""
    await tracing.log_trace(event_type, details)
