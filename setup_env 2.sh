#!/bin/bash
# StosOS Development Environment Setup Script

echo "Setting up StosOS development environment..."
echo "Developed by @parthchhabraa (https://github.com/parthchhabraa)..."

# Create virtual environment
python3 -m venv venv
echo "Virtual environment created"

# Activate virtual environment
source venv/bin/activate
echo "Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To run StosOS, use: python main.py"