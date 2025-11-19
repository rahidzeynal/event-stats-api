#!/bin/bash

# Quick start script for Event Statistics API

echo "Event Statistics API - Quick Start"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting the API server..."
echo "API will be available at: http://localhost:5000"
echo ""
echo "Available endpoints:"
echo "  POST http://localhost:5000/event"
echo "  GET  http://localhost:5000/statistics"
echo "  GET  http://localhost:5000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "==================================="
echo ""

# Run the application
python app.py