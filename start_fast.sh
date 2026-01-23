#!/bin/bash
# Interview Voice Assistant - Instant Start Script

# Navigate to project directory
cd "/home/venkat/InterviewVoiceAssistant"

# Ensure API Key is set if not already in env
export ANTHROPIC_API_KEY="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"

# Start the assistant
./venv/bin/python3 main.py
