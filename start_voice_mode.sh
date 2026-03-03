#!/bin/bash

# Voice Mode Quick Start
# Starts the improved push-to-talk voice interface

set -e

echo "======================================"
echo "  Interview Assistant - Voice Mode"
echo "======================================"
echo ""

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✓ Server already running on port 8000"
else
    echo "Starting web server..."
    python3 web/server.py &
    sleep 2
    echo "✓ Server started on port 8000"
fi

echo ""
echo "======================================"
echo "  VOICE MODE - PUSH-TO-TALK"
echo "======================================"
echo ""
echo "✨ Open in your browser:"
echo "   http://localhost:8000/voice"
echo ""
echo "🎤 How to use:"
echo "   1. Hold SPACE (or click mic button) to speak"
echo "   2. Release to transcribe"
echo "   3. Edit transcription if needed"
echo "   4. Click 'Send Question' to get answer"
echo ""
echo "💡 Features:"
echo "   • ChatGPT-style push-to-talk"
echo "   • Real-time transcription"
echo "   • Edit before sending"
echo "   • Conversation view"
echo "   • No background noise capture"
echo ""
echo "======================================"
echo ""

# Open in default browser (optional)
if command -v xdg-open &> /dev/null; then
    echo "Opening in browser..."
    xdg-open "http://localhost:8000/voice" 2>/dev/null &
elif command -v open &> /dev/null; then
    open "http://localhost:8000/voice"
fi

echo "Press Ctrl+C to stop"
wait
