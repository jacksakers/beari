"""
Flask server for real-time database visualization.
Serves an HTML page with live updates using Server-Sent Events (SSE).
"""

from flask import Flask, render_template, jsonify, Response
from flask_cors import CORS
import json
import time
from typing import Generator
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import DatabaseConnection, get_all_objects, get_properties


app = Flask(__name__)
CORS(app)

# Global event stream clients
clients = []


def get_database_state() -> dict:
    """
    Get current state of entire database.
    
    Returns:
        Dictionary with all objects and their properties
    """
    with DatabaseConnection() as db:
        objects = get_all_objects(db)
        
        # Enrich objects with their properties
        for obj in objects:
            obj['properties'] = get_properties(db, obj['id'])
        
        # Get statistics
        stats = {
            'total_objects': len(objects),
            'nouns': sum(1 for o in objects if o['type'] == 'Noun'),
            'verbs': sum(1 for o in objects if o['type'] == 'Verb'),
            'adjectives': sum(1 for o in objects if o['type'] == 'Adjective'),
            'total_properties': sum(len(o['properties']) for o in objects),
        }
        
        return {
            'objects': objects,
            'stats': stats,
            'timestamp': time.time()
        }


@app.route('/')
def index():
    """Serve the main visualization page."""
    return render_template('viewer.html')


@app.route('/api/database')
def api_database():
    """API endpoint to get full database state."""
    return jsonify(get_database_state())


@app.route('/api/stream')
def stream():
    """Server-Sent Events stream for real-time updates."""
    def event_stream() -> Generator[str, None, None]:
        """Generate SSE events."""
        # Send initial state
        initial_state = get_database_state()
        yield f"data: {json.dumps(initial_state)}\n\n"
        
        # Keep connection alive and send updates
        last_update = time.time()
        while True:
            time.sleep(1)  # Check every second
            
            # Send periodic updates (every 2 seconds)
            if time.time() - last_update > 2:
                current_state = get_database_state()
                yield f"data: {json.dumps(current_state)}\n\n"
                last_update = time.time()
    
    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/object/<name>')
def api_object(name):
    """Get details of a specific object."""
    from db import get_object
    
    with DatabaseConnection() as db:
        obj = get_object(db, name)
        if obj:
            obj['properties'] = get_properties(db, obj['id'])
            return jsonify(obj)
        else:
            return jsonify({'error': 'Object not found'}), 404


def run_viewer(host='127.0.0.1', port=5000, debug=True):
    """
    Run the Flask visualization server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    print(f"\n{'='*70}")
    print(f"🌐 Beari2 Database Viewer")
    print(f"{'='*70}")
    print(f"\nStarting server at http://{host}:{port}")
    print(f"Open your browser and navigate to this URL to view the database in real-time.")
    print(f"\nPress CTRL+C to stop the server.\n")
    
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    run_viewer()
