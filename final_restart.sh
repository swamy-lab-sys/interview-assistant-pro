#!/bin/bash
# Final Fix & Restart Script

echo "=========================================="
echo "  Applying Final Updates..."
echo "=========================================="

# Kill any existing python processes (server/main)
pkill -f "python3 web/server.py"
pkill -f "python3 main.py"

# Get IP
IP=$(hostname -I | awk '{print $1}')

echo "✅ Cleaned up old processes."
# Export User API Key for testing
export ANTHROPIC_API_KEY="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"

echo "✅ Logic: Smart (Concept vs Task)."
echo "✅ Content: Single Code Block (No Split)."
echo "✅ Format: Unified Section (No Headers)."
echo "✅ Style: Human Interview Speech."

echo ""
echo "=========================================="
echo "  🚀 STARTING NEW SESSION"
echo "=========================================="
echo ""
echo "1. Open this URL on Mobile NOW:"
echo "   http://$IP:8000"
echo ""
echo "2. Starting Voice Assistant..."
echo ""

cd /home/venkat/InterviewVoiceAssistant
source venv/bin/activate
python3 main.py voice
