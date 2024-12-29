#!/bin/bash

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Installing Python3..."
    sudo apt update
    sudo apt-get install pip3
    sudo apt install python3 python3-pip -y
else
    echo "Python3 is already installed."
fi
sudo apt install python3 python3-pip -y
# Install PyTorch and related libraries
echo "Installing PyTorch and required libraries..."
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install other required Python libraries
echo "Installing additional Python libraries..."
pip3 install -U numpy pandas matplotlib

echo "Dependencies have been installed successfully!"
