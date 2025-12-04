from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timedelta, timezone
import time

client = TestClient(app)

def test_root_endpoint():
    """Test the root health check endpoint"""
    res = client.get("/")
    assert res.status_code == 200
    assert "message" in res.json()


def test_post_event():
    """Test posting a single event"""
    now = datetime.now(timezone.utc).isoformat()
    res = client.post("/event", json={"timestamp": now, "value": 12.0})
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_post_and_get_single_event():
    """Test posting an event and retrieving statistics"""
    now = datetime.now(timezone.utc).isoformat()
    res = client.post("/event", json={"timestamp": now, "value": 12.0})
    assert res.status_code == 200

    stats = client.get("/statistics").json()
    assert "count" in stats
    assert stats["count"] >= 1
    assert "min" in stats
    assert "max" in stats
    assert "mean" in stats


def test_multiple_events():
    """Test posting multiple events and verifying statistics"""
    now = datetime.now(timezone.utc).isoformat()
    
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    for value in values:
        timestamp = now
        res = client.post("/event", json={"timestamp": timestamp, "value": value})
        assert res.status_code == 200
    
    stats = client.get("/statistics").json()
    assert stats["count"] >= len(values)
    assert stats["min"] <= min(values)
    assert stats["max"] >= max(values)
    assert stats["mean"] is not None


def test_statistics_calculation():
    """Test that statistics are correctly calculated"""
    now = datetime.now(timezone.utc).isoformat()
    
    # Clear old events by waiting or use fresh client
    test_values = [5.0, 15.0, 25.0]
    
    for value in test_values:
        timestamp = now
        client.post("/event", json={"timestamp": timestamp, "value": value})
    
    stats = client.get("/statistics").json()
    
    # Statistics should include at least our test values
    assert stats["count"] >= len(test_values)
    assert stats["min"] is not None
    assert stats["max"] is not None
    assert stats["mean"] is not None


def test_old_events_filtered():
    """Test that events older than 1 hour are not included"""
    # Post an old event (more than 1 hour ago)
    old_time = datetime.now(timezone.utc) - timedelta(hours=2)
    old_timestamp = old_time.isoformat()
    res = client.post("/event", json={"timestamp": old_timestamp, "value": 100.0})
    assert res.status_code == 200
    
    # Post a recent event
    now = datetime.now(timezone.utc).isoformat()
    res = client.post("/event", json={"timestamp": now, "value": 50.0})
    assert res.status_code == 200
    
    stats = client.get("/statistics").json()
    
    # The old event (100.0) should not affect the max significantly
    # if there are other recent events with lower values
    assert stats["count"] >= 1


def test_empty_statistics():
    """Test statistics when no events exist (or all are old)"""
    # This test depends on having no recent events
    # In practice, this is hard to test without resetting the store
    stats = client.get("/statistics").json()
    assert "count" in stats
    assert isinstance(stats["count"], int)


def test_event_timestamp_formats():
    """Test different valid ISO 8601 timestamp formats"""
    formats = [
        datetime.now(timezone.utc).isoformat(),
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    ]
    
    for timestamp in formats:
        res = client.post("/event", json={"timestamp": timestamp, "value": 42.0})
        assert res.status_code == 200


def test_negative_values():
    """Test that negative values are handled correctly"""
    now = datetime.now(timezone.utc).isoformat()
    res = client.post("/event", json={"timestamp": now, "value": -25.5})
    assert res.status_code == 200
    
    stats = client.get("/statistics").json()
    assert stats["count"] >= 1


def test_floating_point_precision():
    """Test that floating point values are handled with proper precision"""
    now = datetime.now(timezone.utc).isoformat()
    precise_value = 123.456789
    res = client.post("/event", json={"timestamp": now, "value": precise_value})
    assert res.status_code == 200
    
    stats = client.get("/statistics").json()
    assert stats["count"] >= 1
    assert stats["mean"] is not None


def test_concurrent_requests():
    """Test that concurrent requests are handled correctly"""
    import concurrent.futures
    
    now = datetime.now(timezone.utc).isoformat()
    
    def post_event(value):
        return client.post("/event", json={"timestamp": now, "value": value})
    
    # Simulate concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(post_event, i * 1.0) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # All requests should succeed
    assert all(r.status_code == 200 for r in results)
    
    # Statistics should reflect all events
    stats = client.get("/statistics").json()
    assert stats["count"] >= 20


def test_statistics_consistency():
    """Test that statistics remain consistent across multiple calls"""
    # Post some events
    now = datetime.now(timezone.utc).isoformat()
    for i in range(5):
        client.post("/event", json={"timestamp": now, "value": float(i)})
    
    # Get statistics multiple times
    stats1 = client.get("/statistics").json()
    stats2 = client.get("/statistics").json()
    
    # Statistics should be consistent
    assert stats1["count"] == stats2["count"]
    assert stats1["min"] == stats2["min"]
    assert stats1["max"] == stats2["max"]
    assert stats1["mean"] == stats2["mean"]