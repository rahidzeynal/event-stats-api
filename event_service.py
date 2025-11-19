"""
Event Service
Handles thread-safe storage and statistics calculation for events
"""

from datetime import datetime, timedelta, timezone
from threading import RLock
from collections import deque
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class EventService:
    """
    Thread-safe service for storing and querying timestamped events.
    
    Uses a deque for efficient insertion and removal of events.
    Automatically cleans up events older than 1 hour.
    """
    
    # Time window for statistics (1 hour)
    TIME_WINDOW = timedelta(hours=1)
    
    def __init__(self):
        """Initialize the event service"""
        # Use deque for O(1) append and efficient iteration
        self._events = deque()
        
        # RLock allows same thread to acquire lock multiple times
        self._lock = RLock()
        
        logger.info("EventService initialized")
    
    def add_event(self, timestamp: datetime, value: float) -> None:
        """
        Add an event to storage.
        
        Args:
            timestamp: Event timestamp (timezone-aware datetime)
            value: Event value (float)
        """
        with self._lock:
            # Ensure timestamp is timezone-aware
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            # Add event as tuple (timestamp, value)
            self._events.append((timestamp, value))
            
            # Clean up old events to prevent unbounded memory growth
            self._cleanup_old_events()
    
    def get_statistics(self) -> Dict[str, Optional[float]]:
        """
        Calculate statistics for events within the last hour.
        
        Returns:
            Dictionary with keys: count, min, max, mean
            If no recent events, min/max/mean are None
        """
        with self._lock:
            # Clean up old events before calculating
            self._cleanup_old_events()
            
            # Get current time (timezone-aware)
            now = datetime.now(timezone.utc)
            cutoff_time = now - self.TIME_WINDOW
            
            # Filter events within the time window
            recent_values = [
                value for timestamp, value in self._events
                if timestamp >= cutoff_time
            ]
            
            # Calculate statistics
            if not recent_values:
                return {
                    "count": 0,
                    "min": None,
                    "max": None,
                    "mean": None
                }
            
            count = len(recent_values)
            min_val = min(recent_values)
            max_val = max(recent_values)
            mean_val = sum(recent_values) / count
            
            return {
                "count": count,
                "min": min_val,
                "max": max_val,
                "mean": mean_val
            }
    
    def _cleanup_old_events(self) -> None:
        """
        Remove events older than the time window.
        Called internally while holding the lock.
        
        This prevents unbounded memory growth by removing stale events.
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now - self.TIME_WINDOW
        
        # Remove old events from the left of the deque
        # Events are roughly time-ordered (assuming clocks are synchronized)
        while self._events and self._events[0][0] < cutoff_time:
            self._events.popleft()
    
    def clear(self) -> None:
        """
        Clear all events. Useful for testing.
        """
        with self._lock:
            self._events.clear()
            logger.info("All events cleared")
    
    def get_event_count(self) -> int:
        """
        Get total number of stored events (for debugging/testing).
        
        Returns:
            Total count of events in storage
        """
        with self._lock:
            return len(self._events)