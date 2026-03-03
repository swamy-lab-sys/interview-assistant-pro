#!/bin/bash
# Quick verification that the fix is in place

echo "========================================="
echo "  Persistence Fix Verification"
echo "========================================="
echo ""

# Check if files were modified
echo "✓ Checking modified files..."

if grep -q "force_clear: bool = False" answer_storage.py; then
    echo "  ✓ answer_storage.py - Updated"
else
    echo "  ✗ answer_storage.py - NOT updated"
    exit 1
fi

if grep -q "load_history_on_startup()" main.py; then
    echo "  ✓ main.py - Updated"
else
    echo "  ✗ main.py - NOT updated"
    exit 1
fi

if grep -q "/api/clear_session" web/server.py; then
    echo "  ✓ web/server.py - Updated"
else
    echo "  ✗ web/server.py - NOT updated"
    exit 1
fi

echo ""
echo "✓ All code changes verified!"
echo ""
echo "========================================="
echo "  Next Steps"
echo "========================================="
echo ""
echo "1. Run visual demo:"
echo "   python3 show_persistence_demo.py"
echo ""
echo "2. Run manual test:"
echo "   ./test_restart_manual.sh"
echo ""
echo "3. Read documentation:"
echo "   cat PERSISTENCE_README.md"
echo ""
echo "========================================="
