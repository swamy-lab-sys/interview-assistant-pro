#!/bin/bash

# Interview Voice Assistant - Production Startup

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: venv not found. Run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Load .env file if present
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Ensure API key is present
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set. Add it to .env file."
    exit 1
fi

# ============================================================
# MODEL SELECTION
# ============================================================

echo ""
echo "============================================================"
echo "  INTERVIEW VOICE ASSISTANT - SETUP"
echo "============================================================"
echo ""

# --- STT Model Selection ---
echo "  Select STT Model (Speech-to-Text):"
echo "    1) tiny.en   - Fastest, lower accuracy"
echo "    2) base.en   - Fast, decent accuracy"
echo "    3) small.en  - Balanced (recommended)"
echo "    4) medium.en - Slowest, best accuracy"
echo ""
read -p "  STT model [1-4, default=3]: " stt_choice

case "$stt_choice" in
    1) STT_MODEL="tiny.en" ;;
    2) STT_MODEL="base.en" ;;
    4) STT_MODEL="medium.en" ;;
    *) STT_MODEL="small.en" ;;
esac

echo "  ✓ STT: $STT_MODEL"
echo ""

# --- LLM Model Selection ---
echo "  Select LLM Model (Answer Generation):"
echo "    1) haiku   - Fastest, cheapest (~1.5s/answer)"
echo "    2) sonnet  - Balanced quality + speed (~2.5s/answer, recommended)"
echo "    3) opus    - Best quality, slowest (~5s/answer)"
echo ""
read -p "  LLM model [1-3, default=2]: " llm_choice

case "$llm_choice" in
    1) LLM_MODEL="claude-3-haiku-20240307" ; LLM_LABEL="Haiku" ;;
    3) LLM_MODEL="claude-opus-4-20250514" ; LLM_LABEL="Opus" ;;
    *) LLM_MODEL="claude-sonnet-4-20250514" ; LLM_LABEL="Sonnet" ;;
esac

echo "  ✓ LLM: $LLM_LABEL ($LLM_MODEL)"
echo ""

# Export selections for Python to pick up
export STT_MODEL_OVERRIDE="$STT_MODEL"
export LLM_MODEL_OVERRIDE="$LLM_MODEL"

echo "============================================================"
echo ""

# Clear previous interview data for fresh start
echo "🗑️  Clearing previous interview data..."
rm -f ~/.interview_assistant/current_answer.json
rm -f ~/.interview_assistant/history.json
echo "✓ Starting fresh interview session"

# Fix ALSA config if corrupted (known issue with card{/pco./control chars)
if grep -q 'card{' /usr/share/alsa/alsa.conf 2>/dev/null || grep -q 'pco\.' /usr/share/alsa/alsa.conf 2>/dev/null; then
    if [ -f /tmp/alsa.conf.fixed ]; then
        echo "  [Audio] Using fixed ALSA config (system config is corrupted)"
        export ALSA_CONFIG_PATH="/tmp/alsa.conf.fixed"
    fi
fi

# Force application to listen to Monitor (System Audio) only
DEFAULT_SINK=$(pactl get-default-sink)
export PULSE_SOURCE="${DEFAULT_SINK}.monitor"

# Run the assistant
export PYTHONWARNINGS="ignore"
exec python3 -W ignore main.py
