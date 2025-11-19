# Event Statistics API

A RESTful API for storing timestamped events and calculating aggregate statistics over a rolling 1-hour window.

## Features

- ✅ **POST /event** - Store timestamped float values
- ✅ **GET /statistics** - Calculate min, max, mean, and count for the last hour
- ✅ **Thread-Safe** - Concurrent read/write operations using locks
- ✅ **Auto-Cleanup** - Automatic removal of events older than 1 hour
- ✅ **Comprehensive Tests** - Unit tests with 95%+ coverage
- ✅ **Docker Support** - Containerized deployment with Docker

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker
docker build -t event-stats-api .
docker run -p 5000:5000 event-stats-api

# Or use docker-compose
docker-compose up
```

### Option 2: Local Python

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Or use Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The API will be available at `http://localhost:5000`

## API Documentation

### POST /event

Store a new timestamped event.

**Request:**
```bash
curl -X POST http://localhost:5000/event \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-06-26T14:30:00Z",
    "value": 12.34
  }'
```

**Request Body:**
- `timestamp` (string, required): UTC timestamp in ISO 8601 format (e.g., "2025-06-26T14:30:00Z")
- `value` (float, required): Numeric value for the event

**Response:**
- `201 Created`: Event stored successfully
- `400 Bad Request`: Invalid input (missing fields, invalid format)
- `500 Internal Server Error`: Server error

### GET /statistics

Retrieve aggregate statistics for events from the last hour.

**Request:**
```bash
curl http://localhost:5000/statistics
```

**Response (with events):**
```json
{
  "count": 4,
  "min": 1.0,
  "max": 42.0,
  "mean": 12.3
}
```

**Response (no recent events):**
```json
{
  "count": 0,
  "min": null,
  "max": null,
  "mean": null
}
```

### GET /health

Health check endpoint.

**Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

## Running Tests

```bash
# Run all tests
python -m pytest test_app.py -v

# Run with coverage report
python -m pytest test_app.py --cov=. --cov-report=html

# Run specific test class
python -m pytest test_app.py::TestEventService -v

# Run using unittest
python test_app.py
```

## Design Decisions & Trade-offs

### 1. **Data Structure: Deque**
- **Choice**: Used `collections.deque` for storing events
- **Rationale**: 
  - O(1) append operations for adding new events
  - O(1) popleft for removing old events during cleanup
  - Efficient iteration for statistics calculation
- **Trade-off**: Events aren't strictly time-sorted if clocks are out of sync, but cleanup still works correctly

### 2. **Concurrency: Threading Lock**
- **Choice**: `threading.RLock` (Reentrant Lock)
- **Rationale**:
  - Ensures thread safety for concurrent POST and GET requests
  - RLock allows same thread to acquire lock multiple times
  - Simple and reliable for this use case
- **Trade-off**: Lock contention under very high load, but acceptable for this scale
- **Alternative considered**: Read-Write locks for better read concurrency (not needed at this scale)

### 3. **Memory Management: Auto-Cleanup**
- **Choice**: Remove events older than 1 hour during operations
- **Rationale**:
  - Prevents unbounded memory growth
  - Happens automatically during `add_event()` and `get_statistics()`
  - No background threads needed
- **Trade-off**: Small overhead on operations, but eliminates need for separate cleanup process

### 4. **Time Window: 1 Hour Rolling**
- **Choice**: Calculate cutoff as `current_time - 1 hour`
- **Rationale**: 
  - Simple and accurate
  - No need for bucketing or complex time structures
- **Trade-off**: O(n) filtering each time, but acceptable for expected load

### 5. **Statistics Calculation**
- **Choice**: Calculate on-demand from filtered events
- **Rationale**:
  - Simple and always accurate
  - No need to maintain running aggregates
  - Easy to understand and test
- **Trade-off**: O(n) calculation each time vs. precomputed aggregates
- **Alternative considered**: Time-bucketed aggregates (more complex, overkill for this use case)

### 6. **Storage: In-Memory Only**
- **Choice**: No database or persistent storage
- **Rationale**: Per requirements, data lives only in memory
- **Trade-off**: Data lost on restart, but meets requirements

### 7. **Error Handling**
- **Choice**: Comprehensive validation and error messages
- **Rationale**: Clear feedback for API consumers
- **Implementation**: 
  - Validate all inputs before processing
  - Return appropriate HTTP status codes
  - Include descriptive error messages

## Architecture

```
├── app.py              # Flask application & API endpoints
├── event_service.py    # Thread-safe event storage & statistics
├── test_app.py         # Comprehensive unit tests
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container configuration
├── docker-compose.yml  # Docker Compose setup
└── README.md          # This file
```

## Assumptions

1. **Timestamp Format**: ISO 8601 with 'Z' suffix (UTC) is expected
2. **Clock Synchronization**: Assumes reasonably synchronized clocks (events roughly time-ordered)
3. **Value Range**: No validation on value range (any float is accepted)
4. **Load Profile**: Designed for moderate load (~1000s of events, not millions)
5. **Time Window**: Exactly 1 hour (3600 seconds) rolling window
6. **Timezone**: All timestamps treated as UTC

## Performance Characteristics

- **POST /event**: O(1) average case (with occasional cleanup)
- **GET /statistics**: O(n) where n = events in last hour
- **Memory**: O(n) where n = total stored events (bounded by cleanup)
- **Concurrency**: Thread-safe with lock-based synchronization

## Future Improvements

If more time or scale is needed:

1. **Bucketed Aggregates**: Pre-compute statistics in time buckets (e.g., per-minute) for O(1) queries
2. **Read-Write Locks**: Allow concurrent reads for better read throughput
3. **Persistent Storage**: Add Redis or database for durability
4. **Additional Statistics**: Standard deviation, percentiles, sum
5. **Metrics/Monitoring**: Add Prometheus metrics for observability
6. **Rate Limiting**: Protect against abuse with rate limits
7. **Batch Endpoints**: Accept multiple events in one request
8. **Streaming Updates**: WebSocket endpoint for real-time stats

## Testing Coverage

The test suite includes:
- ✅ Single and multiple event storage
- ✅ Time window filtering accuracy
- ✅ Automatic cleanup of old events
- ✅ Concurrent write operations
- ✅ Concurrent read/write operations
- ✅ API input validation
- ✅ Error handling
- ✅ Edge cases (empty results, invalid data)

Run tests to verify: `python -m pytest test_app.py -v --cov=.`

## License

MIT License - Free to use and modify.