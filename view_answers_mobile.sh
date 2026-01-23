#!/bin/bash

# Mobile Answers Viewer
# Run this script on mobile (via SSH) to view answers in real-time

ANSWERS_LOG="$HOME/.interview_assistant/answers.log"

echo "============================================================"
echo "INTERVIEW ASSISTANT - MOBILE VIEWER"
echo "============================================================"
echo ""
echo "Viewing answers in real-time from:"
echo "  $ANSWERS_LOG"
echo ""
echo "Press Ctrl+C to stop viewing"
echo ""
echo "============================================================"
echo ""

# Check if log file exists
if [ ! -f "$ANSWERS_LOG" ]; then
    echo "⚠️  Waiting for answers log to be created..."
    echo "   (Start the interview assistant on laptop first)"
    echo ""

    # Wait for file to exist
    while [ ! -f "$ANSWERS_LOG" ]; do
        sleep 1
    done

    echo "✓ Log file detected. Streaming answers..."
    echo ""
fi

# Tail the log file with follow
tail -f "$ANSWERS_LOG"
