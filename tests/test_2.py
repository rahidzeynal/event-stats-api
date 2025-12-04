import requests
from datetime import datetime, timezone

# Post event
response = requests.post(
    "http://localhost:8000/event",
    json={
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "value": 42.5
    }
)
print(response.json())

# Get statistics
stats = requests.get("http://localhost:8000/statistics").json()
print(f"Count: {stats['count']}, Mean: {stats['mean']}")

# Debug: View stored events
debug_info = requests.get("http://localhost:8000/debug/events").json()
print(f"Total events: {debug_info['total_events']}")
for event in debug_info['events']:
    print(f"  - Value: {event['value']}, Age: {event['age_minutes']:.1f} min")