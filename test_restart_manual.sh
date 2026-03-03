#!/bin/bash
# Manual Test Script for Server Restart Persistence
# 
# This script helps you manually test that Q&A history is preserved
# across server restarts.

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

ANSWERS_FILE="$HOME/.interview_assistant/current_answer.json"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Server Restart Persistence Test${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to count Q&A pairs
count_answers() {
    if [ -f "$ANSWERS_FILE" ]; then
        python3 -c "import json; data=json.load(open('$ANSWERS_FILE')); print(len(data) if isinstance(data, list) else 1)"
    else
        echo "0"
    fi
}

# Function to inject test data
inject_test_data() {
    echo -e "${YELLOW}Injecting 4 test Q&A pairs...${NC}"
    python3 << 'EOF'
import json
from pathlib import Path
from datetime import datetime

answers_file = Path.home() / ".interview_assistant" / "current_answer.json"
answers_file.parent.mkdir(parents=True, exist_ok=True)

test_data = []
for i in range(1, 5):
    test_data.append({
        'question': f'What is Python question {i}?',
        'answer': f'This is a detailed answer to Python question {i}. It includes technical details and examples.',
        'timestamp': datetime.now().isoformat(),
        'is_complete': True,
        'metrics': {'test': True, 'llm_ms': 1000}
    })

with open(answers_file, 'w') as f:
    json.dump(test_data, f, indent=2)

print(f"✓ Injected {len(test_data)} test Q&A pairs")
EOF
}

# Function to show current answers
show_answers() {
    if [ -f "$ANSWERS_FILE" ]; then
        echo -e "${BLUE}Current Q&A in storage:${NC}"
        python3 << 'EOF'
import json
from pathlib import Path

answers_file = Path.home() / ".interview_assistant" / "current_answer.json"
if answers_file.exists():
    with open(answers_file, 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            for i, qa in enumerate(data, 1):
                print(f"  {i}. Q: {qa.get('question', 'N/A')[:60]}")
                print(f"     A: {qa.get('answer', 'N/A')[:60]}...")
        else:
            print(f"  1. Q: {data.get('question', 'N/A')[:60]}")
            print(f"     A: {data.get('answer', 'N/A')[:60]}...")
EOF
    else
        echo -e "${RED}  No answers file found${NC}"
    fi
}

echo -e "${YELLOW}STEP 1: Setup Test Data${NC}"
inject_test_data
COUNT_BEFORE=$(count_answers)
echo -e "${GREEN}✓ Setup complete: $COUNT_BEFORE Q&A pairs${NC}\n"

echo -e "${YELLOW}STEP 2: Start Server${NC}"
echo -e "Starting server in background..."
./run.sh > /tmp/interview_server.log 2>&1 &
SERVER_PID=$!
echo -e "Server PID: $SERVER_PID"
echo -e "Waiting for server to start (5 seconds)..."
sleep 5

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✓ Server started successfully${NC}\n"
else
    echo -e "${RED}✗ Server failed to start. Check /tmp/interview_server.log${NC}"
    exit 1
fi

echo -e "${YELLOW}STEP 3: Verify Data Loaded${NC}"
sleep 2
COUNT_AFTER_START=$(count_answers)
show_answers
echo -e "\n${GREEN}✓ After startup: $COUNT_AFTER_START Q&A pairs${NC}\n"

if [ "$COUNT_AFTER_START" -eq "$COUNT_BEFORE" ]; then
    echo -e "${GREEN}✓✓✓ SUCCESS: All Q&A pairs preserved after startup!${NC}\n"
else
    echo -e "${RED}✗✗✗ FAILURE: Expected $COUNT_BEFORE, got $COUNT_AFTER_START${NC}\n"
fi

echo -e "${YELLOW}STEP 4: Restart Server${NC}"
echo -e "Stopping server (PID: $SERVER_PID)..."
kill $SERVER_PID
sleep 3

echo -e "Restarting server..."
./run.sh > /tmp/interview_server.log 2>&1 &
SERVER_PID=$!
echo -e "New server PID: $SERVER_PID"
sleep 5

if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✓ Server restarted successfully${NC}\n"
else
    echo -e "${RED}✗ Server failed to restart${NC}"
    exit 1
fi

echo -e "${YELLOW}STEP 5: Verify Data After Restart${NC}"
sleep 2
COUNT_AFTER_RESTART=$(count_answers)
show_answers
echo -e "\n${GREEN}✓ After restart: $COUNT_AFTER_RESTART Q&A pairs${NC}\n"

# Final verification
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TEST RESULTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Before start:    $COUNT_BEFORE Q&A"
echo -e "After start:     $COUNT_AFTER_START Q&A"
echo -e "After restart:   $COUNT_AFTER_RESTART Q&A"
echo ""

if [ "$COUNT_AFTER_RESTART" -eq "$COUNT_BEFORE" ]; then
    echo -e "${GREEN}✓✓✓ ALL TESTS PASSED ✓✓✓${NC}"
    echo -e "${GREEN}Q&A history is preserved across server restarts!${NC}\n"
    SUCCESS=true
else
    echo -e "${RED}✗✗✗ TEST FAILED ✗✗✗${NC}"
    echo -e "${RED}Q&A history was NOT preserved${NC}\n"
    SUCCESS=false
fi

# Cleanup
echo -e "${YELLOW}Stopping server...${NC}"
kill $SERVER_PID 2>/dev/null || true
sleep 2

echo -e "${YELLOW}Test complete. Server logs: /tmp/interview_server.log${NC}"
echo -e "${YELLOW}Web UI was available at: http://localhost:8000${NC}\n"

if [ "$SUCCESS" = true ]; then
    exit 0
else
    exit 1
fi
