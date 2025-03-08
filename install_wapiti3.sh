#!/bin/bash

# Update system packages
echo "Updating system packages..."
sudo apt update

# Install Python 3 and pip if not already installed
echo "Installing Python3 and pip..."
sudo apt install python3 python3-pip -y

# Upgrade pip to the latest version
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install required dependencies (flask, mitmproxy, werkzeug)
echo "Installing flask, mitmproxy, and werkzeug..."
pip install flask mitmproxy werkzeug==2.0.3

# Install wapiti3
echo "Installing wapiti3..."
pip install wapiti3

# Test wapiti installation
echo "Testing wapiti installation..."
echo "✅ Verifying Wapiti installation..."
if command -v wapiti &> /dev/null; then
    echo "🎉 Wapiti3 successfully installed! Run 'wapiti -h' to get started."
else
    echo "❌ Installation failed!"
fi

