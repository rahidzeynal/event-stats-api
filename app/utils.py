from datetime import datetime, timedelta
from typing import List, Tuple

def is_within_last_hour(timestamp: datetime, reference_time: datetime = None) -> bool:
    """
    Check if a timestamp is within the last hour from a reference time.
    
    Args:
        timestamp: The timestamp to check
        reference_time: Reference time (defaults to current UTC time)
    
    Returns:
        True if timestamp is within the last hour, False otherwise
    """
    if reference_time is None:
        reference_time = datetime.utcnow()
    
    cutoff_time = reference_time - timedelta(hours=1)
    return timestamp >= cutoff_time


def filter_recent_events(events: List[Tuple[datetime, float]], 
                         reference_time: datetime = None) -> List[float]:
    """
    Filter events to only include those from the last hour.
    
    Args:
        events: List of (timestamp, value) tuples
        reference_time: Reference time (defaults to current UTC time)
    
    Returns:
        List of values from events within the last hour
    """
    if reference_time is None:
        reference_time = datetime.utcnow()
    
    cutoff_time = reference_time - timedelta(hours=1)
    return [value for ts, value in events if ts >= cutoff_time]


def calculate_statistics(values: List[float]) -> dict:
    """
    Calculate min, max, mean, and count for a list of values.
    
    Args:
        values: List of float values
    
    Returns:
        Dictionary with count, min, max, and mean
    """
    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None
        }
    
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values)
    }