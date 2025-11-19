"""
Unit Tests for Event Statistics API
Tests API endpoints, event service, thread safety, and edge cases
"""

import unittest
import json
from datetime import datetime, timedelta, timezone
from threading import Thread
import time

from app import app
from event_service import EventService


class TestEventService(unittest.TestCase):
    """Test the EventService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = EventService()
    
    def tearDown(self):
        """Clean up after tests"""
        self.service.clear()
    
    def test_add_and_get_single_event(self):
        """Test adding a single event and retrieving statistics"""
        now = datetime.now(timezone.utc)
        self.service.add_event(now, 10.5)
        
        stats = self.service.get_statistics()
        
        self.assertEqual(stats['count'], 1)
        self.assertEqual(stats['min'], 10.5)
        self.assertEqual(stats['max'], 10.5)
        self.assertEqual(stats['mean'], 10.5)
    
    def test_add_multiple_events(self):
        """Test adding multiple events"""
        now = datetime.now(timezone.utc)
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        for value in values:
            self.service.add_event(now, value)
        
        stats = self.service.get_statistics()
        
        self.assertEqual(stats['count'], 5)
        self.assertEqual(stats['min'], 1.0)
        self.assertEqual(stats['max'], 5.0)
        self.assertEqual(stats['mean'], 3.0)
    
    def test_no_events_returns_empty_stats(self):
        """Test that no events returns count 0 and None for stats"""
        stats = self.service.get_statistics()
        
        self.assertEqual(stats['count'], 0)
        self.assertIsNone(stats['min'])
        self.assertIsNone(stats['max'])
        self.assertIsNone(stats['mean'])
    
    def test_time_window_filtering(self):
        """Test that only events from last hour are included"""
        now = datetime.now(timezone.utc)
        
        # Add event from 2 hours ago (should be excluded)
        old_time = now - timedelta(hours=2)
        self.service.add_event(old_time, 100.0)
        
        # Add event from 30 minutes ago (should be included)
        recent_time = now - timedelta(minutes=30)
        self.service.add_event(recent_time, 50.0)
        
        # Add current event (should be included)
        self.service.add_event(now, 25.0)
        
        stats = self.service.get_statistics()
        
        # Should only include the 2 recent events
        self.assertEqual(stats['count'], 2)
        self.assertEqual(stats['min'], 25.0)
        self.assertEqual(stats['max'], 50.0)
        self.assertEqual(stats['mean'], 37.5)
    
    def test_cleanup_old_events(self):
        """Test that old events are cleaned up"""
        now = datetime.now(timezone.utc)
        
        # Add old events
        for i in range(5):
            old_time = now - timedelta(hours=2, minutes=i)
            self.service.add_event(old_time, float(i))
        
        # Add recent event
        self.service.add_event(now, 999.0)
        
        # Trigger cleanup by getting statistics
        stats = self.service.get_statistics()
        
        # Should only have 1 recent event
        self.assertEqual(stats['count'], 1)
        
        # Total stored events should be cleaned up
        total_events = self.service.get_event_count()
        self.assertEqual(total_events, 1)
    
    def test_concurrent_writes(self):
        """Test thread safety with concurrent writes"""
        now = datetime.now(timezone.utc)
        num_threads = 10
        events_per_thread = 100
        
        def add_events():
            for i in range(events_per_thread):
                self.service.add_event(now, float(i))
        
        threads = [Thread(target=add_events) for _ in range(num_threads)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        stats = self.service.get_statistics()
        
        # Should have all events
        expected_count = num_threads * events_per_thread
        self.assertEqual(stats['count'], expected_count)
    
    def test_concurrent_read_write(self):
        """Test thread safety with concurrent reads and writes"""
        now = datetime.now(timezone.utc)
        results = []
        
        def writer():
            for i in range(50):
                self.service.add_event(now, float(i))
                time.sleep(0.001)
        
        def reader():
            for _ in range(50):
                stats = self.service.get_statistics()
                results.append(stats['count'])
                time.sleep(0.001)
        
        threads = [
            Thread(target=writer),
            Thread(target=writer),
            Thread(target=reader),
            Thread(target=reader)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have completed without errors
        self.assertTrue(len(results) > 0)
        
        # Final count should be accurate
        final_stats = self.service.get_statistics()
        self.assertEqual(final_stats['count'], 100)


class TestAPIEndpoints(unittest.TestCase):
    """Test the Flask API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear events before each test
        from app import event_service
        event_service.clear()
    
    def test_post_event_success(self):
        """Test successful event creation"""
        payload = {
            "timestamp": "2025-06-26T14:30:00Z",
            "value": 12.34
        }
        
        response = self.client.post(
            '/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_post_event_missing_timestamp(self):
        """Test event creation with missing timestamp"""
        payload = {"value": 12.34}
        
        response = self.client.post(
            '/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('timestamp', data['error'].lower())
    
    def test_post_event_missing_value(self):
        """Test event creation with missing value"""
        payload = {"timestamp": "2025-06-26T14:30:00Z"}
        
        response = self.client.post(
            '/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('value', data['error'].lower())
    
    def test_post_event_invalid_timestamp(self):
        """Test event creation with invalid timestamp format"""
        payload = {
            "timestamp": "not-a-timestamp",
            "value": 12.34
        }
        
        response = self.client.post(
            '/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_post_event_invalid_value(self):
        """Test event creation with invalid value"""
        payload = {
            "timestamp": "2025-06-26T14:30:00Z",
            "value": "not-a-number"
        }
        
        response = self.client.post(
            '/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_statistics_empty(self):
        """Test statistics with no events"""
        response = self.client.get('/statistics')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['count'], 0)
        self.assertIsNone(data['min'])
        self.assertIsNone(data['max'])
        self.assertIsNone(data['mean'])
    
    def test_get_statistics_with_events(self):
        """Test statistics with multiple events"""
        now = datetime.now(timezone.utc)
        
        events = [
            {"timestamp": now.isoformat(), "value": 10.0},
            {"timestamp": now.isoformat(), "value": 20.0},
            {"timestamp": now.isoformat(), "value": 30.0}
        ]
        
        for event in events:
            self.client.post(
                '/event',
                data=json.dumps(event),
                content_type='application/json'
            )
        
        response = self.client.get('/statistics')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['count'], 3)
        self.assertEqual(data['min'], 10.0)
        self.assertEqual(data['max'], 30.0)
        self.assertEqual(data['mean'], 20.0)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_404_not_found(self):
        """Test 404 error handling"""
        response = self.client.get('/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_405_method_not_allowed(self):
        """Test 405 error handling"""
        response = self.client.get('/event')
        
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()