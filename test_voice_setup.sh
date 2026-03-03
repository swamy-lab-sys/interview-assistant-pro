#!/bin/bash

# Complete Test & Demo for Voice Mode + Extension
# Tests everything needed for real interview use

set -e

echo "========================================"
echo "  VOICE MODE COMPLETE TEST & DEMO"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Step 1: Check dependencies
echo -e "${BLUE}[1/7] Checking Dependencies...${NC}"
echo ""

check_dependency() {
    if command -v $1 &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 installed"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 not found"
        ((TESTS_FAILED++))
        return 1
    fi
}

check_dependency python3
check_dependency pip
check_dependency curl

echo ""
echo -e "${BLUE}Checking Python packages...${NC}"

check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 installed"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 not installed"
        echo "    Install: pip install $2"
        ((TESTS_FAILED++))
        return 1
    fi
}

check_python_package flask flask
check_python_package pydub pydub
check_python_package numpy numpy

echo ""

# Step 2: Check server
echo -e "${BLUE}[2/7] Checking Server...${NC}"
echo ""

if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Server is running on port 8000"
    ((TESTS_PASSED++))
else
    echo -e "  ${YELLOW}⚠${NC} Server not running"
    echo "  Starting server..."
    python3 web/server.py > /dev/null 2>&1 &
    sleep 3
    
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Server started successfully"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗${NC} Failed to start server"
        ((TESTS_FAILED++))
    fi
fi

echo ""

# Step 3: Test voice endpoint
echo -e "${BLUE}[3/7] Testing Voice Endpoint...${NC}"
echo ""

if curl -s http://localhost:8000/voice | grep -q "Voice Interview Assistant" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} /voice endpoint responding"
    echo -e "  ${GREEN}✓${NC} HTML page loading correctly"
    ((TESTS_PASSED+=2))
else
    echo -e "  ${RED}✗${NC} /voice endpoint not responding"
    ((TESTS_FAILED++))
fi

echo ""

# Step 4: Test API endpoints
echo -e "${BLUE}[4/7] Testing API Endpoints...${NC}"
echo ""

# Test /api/answers
if curl -s http://localhost:8000/api/answers | grep -q "^\[" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} /api/answers responding"
    ((TESTS_PASSED++))
else
    echo -e "  ${RED}✗${NC} /api/answers not responding"
    ((TESTS_FAILED++))
fi

# Test /api/ip
if curl -s http://localhost:8000/api/ip | grep -q "ip" 2>/dev/null; then
    IP=$(curl -s http://localhost:8000/api/ip | grep -o '"ip":"[^"]*"' | cut -d'"' -f4)
    echo -e "  ${GREEN}✓${NC} /api/ip responding (IP: $IP)"
    ((TESTS_PASSED++))
else
    echo -e "  ${RED}✗${NC} /api/ip not responding"
    ((TESTS_FAILED++))
fi

echo ""

# Step 5: Check extension
echo -e "${BLUE}[5/7] Checking Chrome Extension...${NC}"
echo ""

if [ -d "chrome_extension_voice" ]; then
    echo -e "  ${GREEN}✓${NC} Extension directory exists"
    ((TESTS_PASSED++))
    
    if [ -f "chrome_extension_voice/manifest.json" ]; then
        echo -e "  ${GREEN}✓${NC} manifest.json found"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗${NC} manifest.json missing"
        ((TESTS_FAILED++))
    fi
    
    if [ -f "chrome_extension_voice/background.js" ]; then
        echo -e "  ${GREEN}✓${NC} background.js found"
        ((TESTS_PASSED++))
    fi
    
    if [ -f "chrome_extension_voice/popup.html" ]; then
        echo -e "  ${GREEN}✓${NC} popup.html found"
        ((TESTS_PASSED++))
    fi
    
    # Check icons
    for icon in icon16.png icon48.png icon128.png; do
        if [ -f "chrome_extension_voice/$icon" ]; then
            echo -e "  ${GREEN}✓${NC} $icon found"
            ((TESTS_PASSED++))
        else
            echo -e "  ${RED}✗${NC} $icon missing"
            ((TESTS_FAILED++))
        fi
    done
else
    echo -e "  ${RED}✗${NC} Extension directory not found"
    ((TESTS_FAILED++))
fi

echo ""

# Step 6: Documentation check
echo -e "${BLUE}[6/7] Checking Documentation...${NC}"
echo ""

for doc in VOICE_MODE_GUIDE.md EXTENSION_VOICE_GUIDE.md VOICE_MODE_IMPLEMENTATION.md; do
    if [ -f "$doc" ]; then
        echo -e "  ${GREEN}✓${NC} $doc exists"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗${NC} $doc missing"
        ((TESTS_FAILED++))
    fi
done

echo ""

# Step 7: Summary and next steps
echo -e "${BLUE}[7/7] Test Summary${NC}"
echo ""
echo "========================================"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
echo "========================================"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "========================================"
    echo "  READY FOR INTERVIEWS!"
    echo "========================================"
    echo ""
    echo "📋 Quick Start:"
    echo ""
    echo "1. Install Extension:"
    echo "   • Open Chrome → chrome://extensions/"
    echo "   • Enable Developer mode"
    echo "   • Load unpacked → Select: $PWD/chrome_extension_voice"
    echo ""
    echo "2. Test Voice Mode:"
    echo "   • Press Ctrl+Shift+A in Chrome"
    echo "   • Or open: http://localhost:8000/voice"
    echo ""
    echo "3. During Interview:"
    echo "   • Press Ctrl+Shift+A for popup window"
    echo "   • Hold SPACE to record question"
    echo "   • Release to transcribe"
    echo "   • Send to get answer"
    echo ""
    echo "📚 Documentation:"
    echo "   • VOICE_MODE_GUIDE.md - Complete usage guide"
    echo "   • EXTENSION_VOICE_GUIDE.md - Extension setup"
    echo ""
    echo -e "${GREEN}Good luck with your interviews! 🚀${NC}"
else
    echo -e "${YELLOW}⚠ Some tests failed${NC}"
    echo ""
    echo "Common fixes:"
    echo ""
    if ! command -v ffmpeg &> /dev/null; then
        echo "  • Install ffmpeg: sudo apt-get install ffmpeg"
    fi
    echo "  • Install missing packages: pip install -r requirements.txt"
    echo "  • Restart server: python3 web/server.py"
    echo ""
    echo "See TROUBLESHOOTING.md for more help"
fi

echo ""
echo "========================================"
echo ""

# Open browser automatically if all tests passed
if [ $TESTS_FAILED -eq 0 ]; then
    read -p "Open voice mode in browser now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:8000/voice" 2>/dev/null &
        elif command -v open &> /dev/null; then
            open "http://localhost:8000/voice"
        fi
        echo "Opening browser..."
    fi
fi
