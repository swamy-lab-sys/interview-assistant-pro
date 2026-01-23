"""
Web UI for Interview Voice Assistant

Provides a local, read-only, mobile-friendly web interface
to display interview answers on a phone browser.

CRITICAL RULES:
- Runs in background thread (non-blocking)
- Fails gracefully if port is busy
- No authentication (local LAN only)
- No external dependencies
- Read-only (no input fields)
"""

import os
import threading
import logging
from pathlib import Path
from flask import Flask, render_template_string

# Configuration
WEB_PORT = 8080
ANSWERS_DIR = Path.home() / ".interview_assistant"
ANSWERS_LOG = ANSWERS_DIR / "answers.log"

# Disable Flask logging (keep terminal clean during interview)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Flask app
app = Flask(__name__)

# HTML template with inline CSS (mobile-first design)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="1.5">
    <title>Interview Assistant - Live View</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 720px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }

        .header {
            text-align: center;
            margin-bottom: 32px;
            padding-bottom: 16px;
            border-bottom: 2px solid #667eea;
        }

        .header h1 {
            font-size: 24px;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #10b981;
            font-weight: 500;
        }

        .status::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .qa-block {
            margin-bottom: 32px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }

        .qa-block:last-of-type {
            background: #fef3c7;
            border-left-color: #f59e0b;
        }

        .question-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #667eea;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .question-text {
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 16px;
            line-height: 1.5;
        }

        .answer-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .answer-text {
            font-size: 16px;
            line-height: 1.7;
            color: #334155;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .timestamp {
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 12px;
            font-family: 'Courier New', monospace;
        }

        .footer {
            text-align: center;
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
            color: #64748b;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }

        .empty-state h2 {
            font-size: 20px;
            margin-bottom: 8px;
            color: #475569;
        }

        .empty-state p {
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 Interview Assistant</h1>
            <div class="status">Live • Auto-updating</div>
        </div>

        {% if qa_pairs %}
            {% for qa in qa_pairs %}
            <div class="qa-block">
                {% if qa.timestamp %}
                <div class="timestamp">{{ qa.timestamp }}</div>
                {% endif %}
                <div class="question-label">Interviewer</div>
                <div class="question-text">{{ qa.question }}</div>
                <div class="answer-label">Answer</div>
                <div class="answer-text">{{ qa.answer }}</div>
            </div>
            {% endfor %}
        {% else %}
            <div class="empty-state">
                <h2>Waiting for questions...</h2>
                <p>Answers will appear here automatically</p>
            </div>
        {% endif %}

        <div class="footer">
            Auto-refresh every 1.5 seconds
        </div>
    </div>
</body>
</html>
"""


def parse_answers_log():
    """
    Parse answers.log file into structured Q&A pairs

    Returns:
        list of dicts with 'timestamp', 'question', 'answer'
    """
    if not ANSWERS_LOG.exists():
        return []

    try:
        with open(ANSWERS_LOG, 'r', encoding='utf-8') as f:
            content = f.read()

        qa_pairs = []
        current_qa = None

        for line in content.split('\n'):
            line_stripped = line.strip()

            # Skip comments and empty lines
            if line_stripped.startswith('#') or not line_stripped:
                continue

            # Detect timestamp
            if line_stripped.startswith('TIME:'):
                if current_qa:
                    qa_pairs.append(current_qa)
                current_qa = {
                    'timestamp': line_stripped.replace('TIME:', '').strip(),
                    'question': '',
                    'answer': ''
                }

            # Detect question
            elif line_stripped.startswith('INTERVIEWER:'):
                if current_qa:
                    current_qa['question'] = line_stripped.replace('INTERVIEWER:', '').strip()

            # Detect answer start
            elif line_stripped == 'ANSWER:':
                continue

            # Collect answer text
            elif current_qa and current_qa['question'] and not line_stripped.startswith('='):
                if current_qa['answer']:
                    current_qa['answer'] += '\n' + line
                else:
                    current_qa['answer'] = line

        # Add last Q&A pair
        if current_qa and current_qa['question']:
            qa_pairs.append(current_qa)

        return qa_pairs

    except Exception as e:
        print(f"⚠️  Web UI: Error parsing answers log: {e}")
        return []


@app.route('/')
def index():
    """Serve main page with Q&A pairs"""
    qa_pairs = parse_answers_log()
    return render_template_string(HTML_TEMPLATE, qa_pairs=qa_pairs)


def run_flask_server():
    """Run Flask server (called in background thread)"""
    try:
        app.run(host='0.0.0.0', port=WEB_PORT, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        # Silent failure - already logged in start_web_ui
        pass


def start_web_ui():
    """
    Start web UI server in background thread

    SAFETY:
    - Non-blocking (runs in daemon thread)
    - Fails gracefully if port is busy
    - Does NOT crash main app on failure
    """
    try:
        # Ensure answers directory exists
        ANSWERS_DIR.mkdir(parents=True, exist_ok=True)

        # Start Flask in background thread
        thread = threading.Thread(target=run_flask_server, daemon=True)
        thread.start()

        # Give server time to start
        import time
        time.sleep(0.5)

        # Log success (only in verbose mode to keep terminal clean)
        if os.environ.get('VERBOSE'):
            print(f"✓ Web UI started on http://0.0.0.0:{WEB_PORT}")

    except OSError as e:
        # Port already in use - log warning and continue
        if 'Address already in use' in str(e):
            print(f"⚠️  Web UI: Port {WEB_PORT} is busy, continuing without web UI")
        else:
            print(f"⚠️  Web UI: Failed to start ({e}), continuing without web UI")
    except Exception as e:
        # Any other error - log and continue
        print(f"⚠️  Web UI: Unexpected error ({e}), continuing without web UI")


def get_web_ui_url():
    """
    Get web UI URL for display

    Returns:
        str: URL to access web UI
    """
    import socket
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return f"http://{local_ip}:{WEB_PORT}"
    except:
        return f"http://localhost:{WEB_PORT}"
