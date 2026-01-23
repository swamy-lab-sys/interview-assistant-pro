#!/bin/bash

# Interview Voice Assistant - IMMUTABLE SYSTEM PLAYBACK MODE
# Purely silent startup, immediate execution.

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    exit 1
fi

# Ensure API key is present (fail silently to console, but exit)
if [ -z "$ANTHROPIC_API_KEY" ]; then
    exit 1
fi

# Force application to listen to Monitor (System Audio) only
# 1. Get default sink (speaker)
DEFAULT_SINK=$(pactl get-default-sink)
# 2. Append .monitor to target the output stream
export PULSE_SOURCE="${DEFAULT_SINK}.monitor"

# Run the assistant in absolute silent mode
export PYTHONWARNINGS="ignore"
exec python3 -W ignore main.py 2>/dev/null
