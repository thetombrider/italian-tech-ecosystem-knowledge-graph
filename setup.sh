#!/bin/bash

echo "🇮🇹 Italian Tech Ecosystem Graph - Setup Script"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found"

# Check if Neo4j is running
echo "🔍 Checking Neo4j connection..."
if nc -z localhost 7687 2>/dev/null; then
    echo "✅ Neo4j is running on port 7687"
else
    echo "⚠️  Neo4j not detected on port 7687"
    echo "   Please make sure Neo4j is running before starting the app"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created - please edit it with your Neo4j credentials"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Neo4j credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: streamlit run streamlit_app.py"
echo ""
echo "Happy graph building! 🚀"
