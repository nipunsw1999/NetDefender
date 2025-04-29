#!/bin/bash

# Check if Nmap is already installed
if ! command -v nmap &> /dev/null; then
    echo "Installing Nmap..."
    sudo apt update
    sudo apt install -y nmap
    echo "Nmap installation completed."
else
    echo "Nmap is already installed."
fi