#!/bin/bash

echo "============================================================"
echo "MOBILE-ONLY CLEAN VIEW MODE - TEST SUITE"
echo "============================================================"
echo ""
echo "This script tests the mobile-only clean view mode."
echo ""

source venv/bin/activate
export ANTHROPIC_API_KEY="test-key-for-testing"

ANSWERS_LOG="$HOME/.interview_assistant/answers.log"

# Test 1: Mobile Mode (Default)
echo "Test 1: Mobile Mode (laptop terminal clean)"
echo "------------------------------------------------------------"
echo ""
export OUTPUT_MODE="mobile"
echo "OUTPUT_MODE=$OUTPUT_MODE"
echo ""
echo "Sending test question via text mode..."
echo ""

# Send test question
echo "Tell me about your experience with Python" | timeout 30 python3 main.py text 2>&1 | grep -A 5 "Answer sent to mobile" | head -10

echo ""
echo "Checking answers log..."
if [ -f "$ANSWERS_LOG" ]; then
    echo "✅ Answers log created at: $ANSWERS_LOG"
    echo ""
    echo "Last 20 lines of log:"
    tail -20 "$ANSWERS_LOG"
    echo ""
else
    echo "❌ Answers log not found"
    exit 1
fi

echo ""
echo "Test 1 Expected Behavior:"
echo "  ✅ Laptop terminal shows 'Answer sent to mobile'"
echo "  ✅ Laptop terminal does NOT show answer content"
echo "  ✅ Answer written to ~/.interview_assistant/answers.log"
echo ""
echo "============================================================"
echo ""

# Test 2: Terminal Mode (Original behavior)
echo "Test 2: Terminal Mode (original behavior)"
echo "------------------------------------------------------------"
echo ""
export OUTPUT_MODE="terminal"
echo "OUTPUT_MODE=$OUTPUT_MODE"
echo ""

# Clear previous log for clean test
rm -f "$ANSWERS_LOG"

echo "Sending test question..."
echo ""
echo "What is Python?" | timeout 30 python3 main.py text 2>&1 | grep -A 10 "INTERVIEWER:" | head -15

echo ""
echo "Test 2 Expected Behavior:"
echo "  ✅ Answer printed directly to laptop terminal"
echo "  ✅ NO 'Answer sent to mobile' message"
echo "  ✅ Log file should NOT exist or be empty"
echo ""

if [ ! -f "$ANSWERS_LOG" ]; then
    echo "✅ Log file not created (correct for terminal mode)"
else
    if [ ! -s "$ANSWERS_LOG" ]; then
        echo "✅ Log file empty (correct for terminal mode)"
    else
        echo "⚠️  Log file has content (unexpected for terminal-only mode)"
    fi
fi

echo ""
echo "============================================================"
echo ""

# Test 3: Both Mode
echo "Test 3: Both Mode (answers to terminal AND log)"
echo "------------------------------------------------------------"
echo ""
export OUTPUT_MODE="both"
echo "OUTPUT_MODE=$OUTPUT_MODE"
echo ""

# Clear previous log
rm -f "$ANSWERS_LOG"

echo "Sending test question..."
echo ""
echo "Explain decorators" | timeout 30 python3 main.py text 2>&1 | grep -A 10 "INTERVIEWER:" | head -15

echo ""
echo "Checking log file..."
if [ -f "$ANSWERS_LOG" ] && [ -s "$ANSWERS_LOG" ]; then
    echo "✅ Log file created and has content"
else
    echo "❌ Log file missing or empty"
fi

echo ""
echo "Test 3 Expected Behavior:"
echo "  ✅ Answer printed to laptop terminal"
echo "  ✅ Answer also written to log file"
echo "  ✅ Both outputs should have same content"
echo ""
echo "============================================================"
echo ""

# Summary
echo "TEST SUMMARY"
echo "============================================================"
echo ""
echo "Mode Configuration via Environment Variable:"
echo "  export OUTPUT_MODE=mobile    # Laptop clean, log file only"
echo "  export OUTPUT_MODE=terminal  # Original behavior"
echo "  export OUTPUT_MODE=both      # Both outputs"
echo ""
echo "Default: mobile (if OUTPUT_MODE not set)"
echo ""
echo "Mobile Viewing:"
echo "  SSH from mobile and run:"
echo "  ./view_answers_mobile.sh"
echo "  OR"
echo "  tail -f ~/.interview_assistant/answers.log"
echo ""
echo "============================================================"
