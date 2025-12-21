#!/bin/bash

# Setup script for Dark Facts TikTok Generator
# This script helps you get started quickly

echo "🎬 Dark Facts TikTok Generator - Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Please check the error above."
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - PEXELS_API_KEY"
    echo ""
    echo "Get your API keys from:"
    echo "   - OpenAI: https://platform.openai.com/api-keys"
    echo "   - Pexels: https://www.pexels.com/api/"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "======================================"
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. (Optional) Add background music to assets/background_music.mp3"
echo "  3. Run: python main.py"
echo ""
echo "Happy creating! 🌑"
