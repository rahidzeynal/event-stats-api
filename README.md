# Event Statistics API

A thread-safe REST API built with FastAPI to record timestamped events and return aggregated statistics over the past hour.

## Features

- ✅ **Thread-safe in-memory storage** using Python's `threading.Lock`
- ✅ **Timezone-aware datetime handling** with proper UTC support
- ✅ **Automatic cleanup** of events older than 1 hour
- ✅ **Real-time statistics** calculation (min, max, mean, count)
- ✅ **ISO 8601 timestamp** support with automatic timezone conversion
- ✅ **Comprehensive test suite** with 15+ test cases
- ✅ **Docker support** for easy deployment
- ✅ **Debug endpoint** for troubleshooting

## API Endpoints

### `POST /event`

Store a timestamped event with a float value.

**Request Body:**
```json
{
  "timestamp": "2025-11-21T07:45:00Z",
  "value": 42.5
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Event stored successfully",
  "received_timestamp": "2025-11-21T07:45:00+00:00",
  "server_time": "2025-11-21T07:58:25.123456+00:00"
}
```

### `GET /statistics`

Retrieve aggregate statistics for events from the last hour.

**Response:**
```json
{
  "count": 4,
  "min": 1.0,
  "max": 42.5,
  "mean": 12.3
}
```

If no recent events exist:
```json
{
  "count": 0,
  "min": null,
  "max": null,
  "mean": null
}
```

### `GET /debug/events`

Debug endpoint to view all stored events and their status.

**Response:**
```json
{
  "current_time": "2025-11-21T08:00:00+00:00",
  "cutoff_time": "2025-11-21T07:00:00+00:00",
  "total_events": 2,
  "events": [
    {
      "timestamp": "2025-11-21T07:45:00+00:00",
      "value": 42.5,
      "is_recent": true,
      "age_minutes": 15.0
    }
  ]
}
```

### `GET /`

Health check endpoint with server time information.

## Installation & Setup

### Prerequisites

- Python 3.10+
- Poetry (recommended) or pip
- Docker (optional, for containerized deployment)

### Using Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Run the application
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app --cov-report=html
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic pytest httpx

# Run the application
uvicorn app.main:app --reload

# Run tests
pytest
```

### Using Docker

```bash
# Build the image
docker build -t stats-api .

# Run the container
docker run -p 8000:8000 stats-api

# Or use docker-compose
docker-compose up
```

The application will be available at `http://localhost:8000`

## Testing

The project includes comprehensive tests covering:

- ✅ Basic event posting and retrieval
- ✅ Multiple events and statistics calculation
- ✅ Time window filtering (1-hour boundary)
- ✅ Timezone-aware datetime handling
- ✅ Edge cases (empty stats, negative values, floating-point precision)
- ✅ Concurrent request handling
- ✅ Different timestamp formats
- ✅ Statistics consistency

Run tests with:
```bash
poetry run pytest -v
```

For coverage report:
```bash
poetry run pytest --cov=app --cov-report=term-missing
```

## Architecture & Design Decisions

### Timezone-Aware DateTime Handling

The API properly handles timezone-aware datetimes:
- Uses `datetime.now(timezone.utc)` instead of deprecated `utcnow()`
- Automatically converts naive datetimes to UTC
- Ensures all timestamp comparisons are timezone-aware
- Pydantic validator normalizes all incoming timestamps to UTC

### Thread Safety

The `EventStore` class uses `threading.Lock` to ensure thread-safe operations:
- All read/write operations on the event deque are protected
- Prevents race conditions during concurrent API requests
- Maintains data consistency across multiple threads

### Memory Management

- Uses `collections.deque` for efficient O(1) append and popleft operations
- Automatically cleans up events older than 1 hour during statistics retrieval
- Prevents unbounded memory growth in long-running applications

### Time Filtering

- Calculates cutoff time as `current_time - 1 hour` (rolling window)
- Only includes events with `timestamp >= cutoff_time`
- Uses UTC timezone consistently to avoid timezone issues
- All timestamps stored with timezone information

### Data Structure

Events are stored as tuples: `(timestamp: datetime, value: float)`
- Timestamps are timezone-aware (UTC)
- Efficient storage and retrieval
- Natural ordering by insertion time
- Easy filtering by timestamp

### Statistics Calculation

- Uses Python's built-in `statistics.mean()` for accurate floating-point arithmetic
- Returns `null` for statistics when no events exist
- Handles edge cases (single event, negative values, etc.)

## Project Structure

```
stats-api/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Pydantic models with timezone validation
│   ├── storage.py           # Thread-safe event storage
│   └── utils.py             # Helper functions
├── tests/
│   └── test_main.py         # Comprehensive test suite
├── pyproject.toml           # Poetry dependencies
├── poetry.lock              # Locked dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
└── README.md                # This file
```

## API Usage Examples

### Using curl

```bash
# Check server health and time
curl http://localhost:8000/

# Post an event
curl -X POST "http://localhost:8000/event" \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2025-12-04T04:45:00Z", "value": 42.5}'

# Get statistics
curl http://localhost:8000/statistics

# Debug: View all stored events
curl http://localhost:8000/debug/events
```

### Using Python requests

```python
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
```

### Using httpx (async)

```python
import httpx
import asyncio
from datetime import datetime, timezone

async def main():
    async with httpx.AsyncClient() as client:
        # Post event
        response = await client.post(
            "http://localhost:8000/event",
            json={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "value": 42.5
            }
        )
        print(response.json())
        
        # Get statistics
        stats = await client.get("http://localhost:8000/statistics")
        print(stats.json())

asyncio.run(main())
```

## Troubleshooting

### Events not showing in statistics

1. **Check server time and event timestamp:**
   ```bash
   curl http://localhost:8000/
   ```

2. **Use the debug endpoint:**
   ```bash
   curl http://localhost:8000/debug/events
   ```
   This shows:
   - Current server time
   - Cutoff time (1 hour ago)
   - All stored events with their age
   - Whether each event is considered "recent"

3. **Verify timezone:**
   - Ensure timestamps include timezone info (e.g., 'Z' or '+00:00')
   - Server uses UTC timezone
   - Events older than 1 hour from current time are filtered out

### Common Issues

**Issue:** Statistics return count: 0 even after posting events

**Solutions:**
- Check that event timestamps are within the last hour
- Verify timestamp format includes timezone (Z suffix or +00:00)
- Use `/debug/events` endpoint to inspect stored events
- Ensure server time matches expected timezone (UTC)

**Issue:** Container time differs from local time

**Solution:**
- All timestamps should be in UTC
- The API automatically converts timezones
- Use `datetime.now(timezone.utc)` in client code

## Performance Considerations

- **Time Complexity:**
  - Store event: O(1)
  - Get statistics with cleanup: O(n) where n is the number of old events to remove
  - Statistics calculation: O(m) where m is the number of recent events

- **Space Complexity:** O(n) where n is the number of events in the last hour

- **Concurrency:** Thread-safe for multiple concurrent requests

## Assumptions & Trade-offs

### Assumptions
1. Events can arrive out of order (older timestamps after newer ones)
2. UTC timezone is used consistently across all operations
3. The 1-hour window is a rolling window from "now"
4. Events with the same timestamp are allowed
5. Naive datetimes (without timezone) are assumed to be UTC

### Trade-offs
1. **In-memory storage:** Fast but not persistent across restarts
2. **Cleanup during retrieval:** Slightly slower GET requests but prevents memory leaks
3. **Global lock:** Simple thread-safety but could be optimized with read-write locks for high concurrency
4. **No event validation:** Accepts any timestamp (past or future)
5. **Debug endpoint in production:** Useful for troubleshooting but should be disabled in production

## Production Deployment Considerations

### Security
- Remove or protect the `/debug/events` endpoint in production
- Add authentication/authorization (e.g., API keys, JWT tokens)
- Implement rate limiting to prevent abuse
- Add input validation for reasonable timestamp ranges

### Monitoring
- Add logging for all operations
- Implement health checks for container orchestration
- Add Prometheus metrics endpoint
- Monitor memory usage and event count

### Optimization
- Implement read-write locks for better concurrency under high load
- Consider background cleanup task instead of cleanup-on-read
- Add caching for statistics if read-heavy workload
- Implement event batching for bulk inserts

### Persistence (Future Enhancement)
- Add database backend (PostgreSQL, Redis) for durability
- Implement event replay from persistent storage on restart
- Add data retention policies

## Future Enhancements

- [ ] Add persistent storage (database backend)
- [ ] Implement read-write locks for better concurrency
- [ ] Add endpoint to query statistics for custom time ranges
- [ ] Add standard deviation and percentiles
- [ ] Implement event batching for bulk inserts
- [ ] Add rate limiting and authentication
- [ ] Add Prometheus metrics endpoint
- [ ] Implement background cleanup task
- [ ] Add data export functionality (CSV, JSON)
- [ ] Support for multiple time windows (5 min, 15 min, 1 hour, 24 hours)
- [ ] Event deduplication based on timestamp + value

## Development Notes

### Python Version Compatibility
- Requires Python 3.10+ for timezone.utc support
- Uses modern Pydantic v2 validation
- Follows current datetime best practices (no deprecated utcnow())

### Testing Strategy
- Unit tests for individual components
- Integration tests for API endpoints
- Concurrency tests for thread safety
- Edge case coverage for robust behavior

### Code Quality
- Type hints throughout the codebase
- Docstrings for all public functions
- Follows PEP 8 style guidelines
- Comprehensive error handling

## License

This project is part of a take-home assignment.

## Contact

For questions or feedback, please reach out to the development team.

---

**Last Updated:** November 2025  
**API Version:** 1.0.0  
**Python Version:** 3.10+