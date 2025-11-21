from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from app.models import Event
from app import storage

app = FastAPI(
    title="Event Statistics API",
    description="REST API to record timestamped events and return aggregated statistics",
    version="1.0.0"
)

@app.post("/event", status_code=200)
def receive_event(event: Event):
    """
    Store a timestamped event with a float value.
    
    - **timestamp**: UTC ISO 8601 format (e.g., "2025-06-26T14:30:00Z")
    - **value**: Float value to be stored
    """
    try:
        # Debug: print received timestamp
        print(f"Received event - Timestamp: {event.timestamp}, Value: {event.value}")
        print(f"Timestamp type: {type(event.timestamp)}, tzinfo: {event.timestamp.tzinfo}")
        print(f"Current server time: {datetime.now(timezone.utc)}")
        
        storage.store_event(event.timestamp, event.value)
        return {
            "status": "success", 
            "message": "Event stored successfully",
            "received_timestamp": event.timestamp.isoformat(),
            "server_time": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        print(f"Error storing event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store event: {str(e)}")


@app.get("/statistics")
def get_statistics():
    """
    Return aggregate statistics for all events from the last hour.
    
    Returns:
    - **count**: Number of events in the last hour
    - **min**: Minimum value (null if no events)
    - **max**: Maximum value (null if no events)
    - **mean**: Average value (null if no events)
    """
    try:
        stats = storage.get_recent_stats()
        print(f"Statistics requested - Current time: {datetime.now(timezone.utc)}")
        print(f"Stats: {stats}")
        return stats
    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@app.get("/debug/events")
def debug_events():
    """Debug endpoint to see all stored events"""
    from datetime import timedelta
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
    
    events_info = []
    for ts, value in storage._store._events:
        events_info.append({
            "timestamp": ts.isoformat(),
            "value": value,
            "is_recent": ts >= cutoff_time,
            "age_minutes": (datetime.now(timezone.utc) - ts).total_seconds() / 60
        })
    
    return {
        "current_time": datetime.now(timezone.utc).isoformat(),
        "cutoff_time": cutoff_time.isoformat(),
        "total_events": len(events_info),
        "events": events_info
    }


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "Event Statistics API is running",
        "server_time": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "POST /event": "Store a new event",
            "GET /statistics": "Get statistics for the last hour",
            "GET /debug/events": "Debug: View all stored events"
        }
    }