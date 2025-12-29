#!/bin/bash

echo "🚀 Starting Financial Calculator Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment using Python 3.12..."
    /usr/local/bin/python3.12 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies (using --upgrade to ensure stability)
echo "Installing/Updating dependencies..."
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn pydantic reportlab "numpy>=1.26.0" "matplotlib>=3.8.0"

# Clear port 8000 if it's in use
echo "Checking port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
