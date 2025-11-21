from datetime import datetime, timedelta, timezone
from typing import List, Optional
from threading import Lock
from collections import deque
import statistics

class EventStore:
    """Thread-safe in-memory store for timestamped float events"""
    
    def __init__(self):
        self._events = deque()  # Store (timestamp, value) tuples
        self._lock = Lock()
    
    def store_event(self, timestamp: datetime, value: float) -> None:
        """Store an event with timestamp and value"""
        with self._lock:
            # Ensure timestamp is timezone-aware (UTC)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            self._events.append((timestamp, value))
    
    def get_recent_stats(self) -> dict:
        """Return statistics for events from the last hour"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        with self._lock:
            # Filter events from the last hour
            recent_values = [
                value for ts, value in self._events 
                if ts >= cutoff_time
            ]
            
            # Clean up old events (older than 1 hour) to prevent memory growth
            while self._events and self._events[0][0] < cutoff_time:
                self._events.popleft()
        
        # Calculate statistics
        if not recent_values:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "mean": None
            }
        
        return {
            "count": len(recent_values),
            "min": min(recent_values),
            "max": max(recent_values),
            "mean": statistics.mean(recent_values)
        }


# Global instance
_store = EventStore()


def store_event(timestamp: datetime, value: float) -> None:
    """Store the event"""
    _store.store_event(timestamp, value)


def get_recent_stats() -> dict:
    """Return stats for events from the last hour"""
    return _store.get_recent_stats()