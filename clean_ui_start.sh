#!/bin/bash
# Quick Start for Clean Web UI (V3)

echo "=========================================="
echo "  Interview Assistant - Clean UI Mode"
echo "=========================================="
echo ""

# Get IP address
IP=$(hostname -I | awk '{print $1}')

echo "✨ NEW FEATURES ACTIVATED:"
echo "   • Clear Bullet Points for Theory"
echo "   • Separate Code Blocks with Syntax Highlighting"
echo "   • Clean Dark Theme"
echo "   • No Large Walls of Text"
echo ""
echo "=========================================="
echo ""
echo "📱 1. START THE WEB SERVER:"
echo "   cd /home/venkat/InterviewVoiceAssistant"
echo "   source venv/bin/activate"
echo "   python3 web/server.py"
echo ""
echo "   👉 Open on Mobile: http://$IP:8000"
echo ""
echo "=========================================="
echo ""
echo "🎙️  2. START THE INTERVIEW ASSISTANT:"
echo "   # Open a NEW terminal window"
echo "   cd /home/venkat/InterviewVoiceAssistant"
echo "   source venv/bin/activate"
echo "   python3 main.py voice"
echo ""
echo "=========================================="
