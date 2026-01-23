#!/usr/bin/env python3
"""
Web Server for Interview Voice Assistant

Provides real-time UI for viewing interview answers.

Features:
- Server-Sent Events (SSE) for real-time updates
- Syntax highlighting for code blocks
- Mobile-first responsive design
- Performance metrics display
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from flask import Flask, render_template, Response, jsonify

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import answer_storage

# Import debug logger
try:
    import debug_logger as dlog
    LOGGING_ENABLED = True
except ImportError:
    LOGGING_ENABLED = False
    class DlogStub:
        def log(self, *args, **kwargs): pass
    dlog = DlogStub()

# Configuration
DEFAULT_PORT = 8000
app = Flask(__name__)

# Disable Flask logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
def index():
    """Serve main page."""
    return render_template('index.html')


@app.route('/api/answers')
def get_answers():
    """Get all answers."""
    answers = answer_storage.get_all_answers()
    return jsonify(answers)


@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    """Upload resume file."""
    from flask import request
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        try:
            # Import config here to avoid circular imports if any
            from config import RESUME_PATH
            
            # Save to resume.txt
            save_path = Path.cwd() / RESUME_PATH
            file.save(save_path)
            return jsonify({'success': True, 'message': 'Resume uploaded successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Unknown error'}), 400


@app.route('/api/stream')
def stream():
    """SSE stream for real-time updates - OPTIMIZED for low latency."""
    def event_stream():
        last_data = ""
        while True:
            answers = answer_storage.get_all_answers()
            current_data = json.dumps(answers)

            if current_data != last_data:
                yield f"data: {current_data}\n\n"
                last_data = current_data

            time.sleep(0.05)  # 50ms polling - reduced from 100ms

    response = Response(event_stream(), mimetype='text/event-stream')
    # Disable buffering for real-time streaming
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable nginx buffering
    response.headers['Connection'] = 'keep-alive'
    return response


@app.route('/api/logs')
def get_logs():
    """Get recent debug logs."""
    try:
        log_file = Path.home() / ".interview_assistant" / "logs" / "debug.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                return jsonify({"logs": [l.strip() for l in lines[-100:]]})
        return jsonify({"logs": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/performance')
def get_performance():
    """Get recent performance logs."""
    try:
        log_file = Path.home() / ".interview_assistant" / "logs" / "performance.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                return jsonify({"logs": [l.strip() for l in lines[-50:]]})
        return jsonify({"logs": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Interview Assistant Web UI')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    args = parser.parse_args()

    print("=" * 60)
    print("Interview Voice Assistant - Web UI Server")
    print("=" * 60)
    print(f"\nServer: http://{args.host}:{args.port}")
    print(f"Mobile: http://<your-ip>:{args.port}")
    print(f"Data: {answer_storage.get_answers_file_path()}")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60 + "\n")

    try:
        # Use threaded mode for better SSE performance
        from werkzeug.serving import WSGIRequestHandler
        WSGIRequestHandler.protocol_version = "HTTP/1.1"  # Enable keep-alive
        app.run(host=args.host, port=args.port, debug=False, threaded=True, use_reloader=False)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\nError: Port {args.port} in use")
            print(f"Try: python3 web/server.py --port {args.port + 1}")
        else:
            print(f"\nError: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nServer stopped")
        sys.exit(0)


if __name__ == '__main__':
    main()
