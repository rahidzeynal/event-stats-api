"""
Event Statistics API
Main Flask application with POST /event and GET /statistics endpoints
"""

from flask import Flask, request, jsonify
from datetime import datetime
import logging

from event_service import EventService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
event_service = EventService()


@app.route('/event', methods=['POST'])
def post_event():
    """
    POST /event
    
    Accepts a JSON payload with timestamp and value:
    {
        "timestamp": "2025-06-26T14:30:00Z",
        "value": 12.34
    }
    
    Returns:
        201: Event created successfully
        400: Invalid request data
    """
    try:
        data = request.get_json()
        
        # Validate request data
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        if 'timestamp' not in data:
            return jsonify({"error": "Missing 'timestamp' field"}), 400
        
        if 'value' not in data:
            return jsonify({"error": "Missing 'value' field"}), 400
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            return jsonify({"error": f"Invalid timestamp format. Use ISO 8601 (e.g., '2025-06-26T14:30:00Z'): {str(e)}"}), 400
        
        # Validate value
        try:
            value = float(data['value'])
        except (ValueError, TypeError) as e:
            return jsonify({"error": f"Invalid value. Must be a number: {str(e)}"}), 400
        
        # Store the event
        event_service.add_event(timestamp, value)
        
        logger.info(f"Event added: timestamp={timestamp}, value={value}")
        
        return jsonify({"message": "Event created successfully"}), 201
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/statistics', methods=['GET'])
def get_statistics():
    """
    GET /statistics
    
    Returns aggregate statistics for events from the last hour:
    {
        "count": 4,
        "min": 1.0,
        "max": 42.0,
        "mean": 12.3
    }
    
    If no recent events, returns:
    {
        "count": 0,
        "min": null,
        "max": null,
        "mean": null
    }
    
    Returns:
        200: Statistics calculated successfully
        500: Internal server error
    """
    try:
        stats = event_service.get_statistics()
        
        logger.info(f"Statistics requested: {stats}")
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == '__main__':
    # Run the Flask app
    # In production, use a proper WSGI server like Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=False)