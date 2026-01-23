#!/bin/bash

echo "=================================="
echo "Interview Voice Assistant - Setup"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
echo "This may take several minutes..."
pip install -r requirements.txt

# Check for GPU
echo ""
echo "Checking for GPU support..."
python3 -c "import torch; print('✓ CUDA available:', torch.cuda.is_available())" 2>/dev/null || echo "⚠ PyTorch not installed yet"

# Create resume.txt if it doesn't exist
if [ ! -f "resume.txt" ]; then
    echo ""
    echo "Creating sample resume.txt..."
    cat > resume.txt << 'EOF'
Sample Resume

Name: [Your Name]
Experience: [Your Experience]
Skills: Python, Machine Learning, Web Development
Education: [Your Education]

Add your actual resume content here.
EOF
    echo "✓ Sample resume.txt created"
else
    echo "✓ resume.txt already exists"
fi

# Check environment variables
echo ""
echo "Checking environment variables..."

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠ ANTHROPIC_API_KEY not set"
    echo "  Get your key from: https://console.anthropic.com/"
    echo "  Set it with: export ANTHROPIC_API_KEY='your-key'"
else
    echo "✓ ANTHROPIC_API_KEY is set"
fi

if [ -z "$HUGGINGFACE_TOKEN" ]; then
    echo "⚠ HUGGINGFACE_TOKEN not set (optional)"
    echo "  For advanced speaker diarization"
    echo "  Get token from: https://huggingface.co/settings/tokens"
else
    echo "✓ HUGGINGFACE_TOKEN is set"
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit resume.txt with your information"
echo "2. Set ANTHROPIC_API_KEY environment variable"
echo "3. Run: ./run.sh [text|voice|streaming]"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  export ANTHROPIC_API_KEY='your-key'"
echo "  python main.py [text|voice|streaming]"
echo ""
