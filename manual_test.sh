#!/bin/bash

# Manual Testing Script for Event Statistics API
# This script demonstrates the API functionality with example requests

BASE_URL="http://localhost:5000"

echo "================================"
echo "Event Statistics API - Manual Test"
echo "================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s $BASE_URL/health | jq .
echo ""

# Test 2: Get Statistics (empty)
echo "2. Getting statistics (should be empty)..."
curl -s $BASE_URL/statistics | jq .
echo ""

# Test 3: Post some events
echo "3. Posting events..."

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

curl -s -X POST $BASE_URL/event \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\": \"$TIMESTAMP\", \"value\": 10.5}" | jq .

curl -s -X POST $BASE_URL/event \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\": \"$TIMESTAMP\", \"value\": 20.5}" | jq .

curl -s -X POST $BASE_URL/event \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\": \"$TIMESTAMP\", \"value\": 30.5}" | jq .

curl -s -X POST $BASE_URL/event \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\": \"$TIMESTAMP\", \"value\": 40.5}" | jq .

echo ""

# Test 4: Get Statistics (with data)
echo "4. Getting statistics (should show 4 events)..."
curl -s $BASE_URL/statistics | jq .
echo ""

# Test 5: Post invalid event (missing timestamp)
echo "5. Testing error handling (missing timestamp)..."
curl -s -X POST $BASE_URL/event \
  -H "Content-Type: application/json" \
  -d '{"value": 99.9}' | jq .
echo ""

# Test 6: Post invalid event (bad timestamp format)
echo "6. Testing error handling (invalid timestamp)..."
curl -s -X POST $BASE_URL/event \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "not-a-date", "value": 99.9}' | jq .
echo ""

# Test 7: Post invalid event (missing value)
echo "7. Testing error handling (missing value)..."
curl -s -X POST $BASE_URL/event \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\": \"$TIMESTAMP\"}" | jq .
echo ""

# Test 8: Post old event (2 hours ago)
echo "8. Posting old event (2 hours ago - should be filtered out)..."
OLD_TIMESTAMP=$(date -u -d '2 hours ago' +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v-2H +"%Y-%m-%dT%H:%M:%SZ")
curl -s -X POST $BASE_URL/event \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\": \"$OLD_TIMESTAMP\", \"value\": 1000.0}" | jq .
echo ""

# Test 9: Get Statistics again (should still be 4, not 5)
echo "9. Getting statistics again (old event should be excluded)..."
curl -s $BASE_URL/statistics | jq .
echo ""

echo "================================"
echo "Manual testing complete!"
echo "================================"