#!/bin/bash
# Quick Start Script for Web UI

echo "=================================================="
echo "  Interview Voice Assistant - Web UI Quick Start"
echo "=================================================="
echo ""

# Get IP address
IP=$(hostname -I | awk '{print $1}')

echo "📱 MOBILE WEB UI"
echo ""
echo "1. Start the app:"
echo "   cd /home/venkat/InterviewVoiceAssistant"
echo "   source venv/bin/activate"
echo "   python3 main.py voice"
echo ""
echo "2. Open on your phone:"
echo "   http://$IP:8080"
echo ""
echo "=================================================="
echo ""
echo "✅ Web UI Features:"
echo "   • Auto-refreshes every 1.5 seconds"
echo "   • Mobile-optimized layout"
echo "   • Clean, readable typography"
echo "   • Latest answer highlighted"
echo ""
echo "🧪 Test the Web UI:"
echo "   python3 test_web_ui.py"
echo ""
echo "📖 Full Documentation:"
echo "   cat WEB_UI_GUIDE.md"
echo ""
echo "=================================================="
