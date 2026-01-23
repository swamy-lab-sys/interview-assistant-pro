#!/bin/bash
# YouTube Test Helper
# Usage: ./test_youtube.sh "https://youtube.com/watch?v=..."

if [ -z "$1" ]; then
    echo "Usage: ./test_youtube.sh <youtube_url>"
    echo "Example: ./test_youtube.sh 'https://youtube.com/watch?v=dQw4w9WgXcQ'"
    exit 1
fi

URL="$1"

echo "=========================================="
echo "YouTube Interview Assistant Test"
echo "=========================================="
echo ""
echo "1. Opening YouTube video in browser..."
echo "   URL: $URL"
echo ""
echo "2. Starting Interview Assistant..."
echo ""
echo "Instructions:"
echo "  - The assistant will listen to your system audio"
echo "  - Play the YouTube video"
echo "  - When a question is asked, the assistant will:"
echo "    * Capture the audio"
echo "    * Transcribe it"
echo "    * Validate it's a real question"
echo "    * Generate and display the answer"
echo ""
echo "  - Press Ctrl+C to stop"
echo ""
echo "=========================================="
echo ""

# Open YouTube in browser
xdg-open "$URL" 2>/dev/null || open "$URL" 2>/dev/null || echo "Please open: $URL"

sleep 3

# Start the assistant
cd "$(dirname "$0")"
./venv/bin/python3 main.py
