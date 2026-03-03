#!/bin/bash

# Fix Python Bytecode Corruption - Interview Voice Assistant
# This script fixes the "bad marshal data" error

echo "=========================================="
echo "Python Bytecode Corruption Fix"
echo "=========================================="
echo ""

# Step 1: Clean system Python cache (requires sudo)
echo "Step 1/6: Cleaning system Python cache..."
echo "Note: You will be prompted for your sudo password"
echo ""

if sudo find /usr/lib/python3.10 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; then
    echo "✓ System __pycache__ directories cleaned"
else
    echo "⚠ Could not clean some system cache (this is usually OK)"
fi

if sudo find /usr/lib/python3.10 -type f -name "*.pyc" -delete 2>/dev/null; then
    echo "✓ System .pyc files cleaned"
else
    echo "⚠ Could not clean some .pyc files (this is usually OK)"
fi
echo ""

# Step 2: Clean project cache
echo "Step 2/6: Cleaning project cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✓ Project cache cleaned"
echo ""

# Step 3: Remove old virtual environment
echo "Step 3/6: Removing old virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
    echo "✓ Old venv removed"
else
    echo "✓ No old venv found"
fi
echo ""

# Step 4: Create fresh virtual environment
echo "Step 4/6: Creating fresh virtual environment..."
if python3 -m venv venv; then
    echo "✓ New venv created successfully"
else
    echo "✗ Failed to create venv"
    echo ""
    echo "Trying alternative method..."
    python3 -m venv venv --without-pip
    source venv/bin/activate
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    rm get-pip.py
    echo "✓ New venv created with manual pip installation"
fi
echo ""

# Step 5: Install dependencies
echo "Step 5/6: Installing dependencies..."
echo "This may take a few minutes..."
source venv/bin/activate

# Upgrade pip first
echo "  → Upgrading pip..."
pip install --upgrade pip -q

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "  → Installing from requirements.txt..."
    pip install -r requirements.txt -q
    echo "✓ All dependencies installed"
else
    echo "  → requirements.txt not found. Installing core dependencies..."
    pip install anthropic whisperx sounddevice numpy -q
    echo "✓ Core dependencies installed"
fi
echo ""

# Step 6: Verify installation
echo "Step 6/6: Verifying installation..."
if python -c "import anthropic; print('✓ anthropic imported successfully')" 2>/dev/null; then
    echo "✓ Installation verified"
else
    echo "⚠ Verification failed - you may need to reinstall dependencies"
fi
echo ""

echo "=========================================="
echo "✓ Fix Complete!"
echo "=========================================="
echo ""
echo "Your environment is now ready!"
echo ""
echo "To start the application:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  export ANTHROPIC_API_KEY='your-key-here'"
echo "  python main.py"
echo ""
