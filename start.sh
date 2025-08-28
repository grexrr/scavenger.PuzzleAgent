#!/bin/bash

# scavenger.RiddleAgent Start Script
echo "🎯 Starting scavenger.RiddleAgent..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create .env file with required configuration."
    echo "   See README.md for environment configuration details."
fi

# Check if MongoDB is running
echo "🔍 Checking MongoDB connection..."
python3 -c "
from pymongo import MongoClient
import sys
try:
    client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
    client.server_info()
    print('✅ MongoDB connection successful')
except Exception as e:
    print('❌ MongoDB connection failed:', str(e))
    print('   Please start MongoDB before launching the service.')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Start the Flask application
echo "🚀 Starting Flask application on port 5001..."
echo "   Access the API at: http://localhost:5001"
echo "   Press Ctrl+C to stop the service"
echo ""

python app.py 