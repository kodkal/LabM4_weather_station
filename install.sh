#!/bin/bash
# =====================================================
# Weather Station Lab - Bootstrap Installer
# One-line installation script for students
# 
# Usage:
#   curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash
# =====================================================

set -e

# Configuration
REPO_URL="https://github.com/kodkal/LabM4_weather_station.git"
INSTALL_DIR="$HOME/LabM4_weather_station"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Simple banner
echo -e "${BLUE}"
echo "================================="
echo " Weather Station Lab - Module 4"
echo "      UVU IoT Security"
echo "================================="
echo -e "${NC}"

# Check if running on Raspberry Pi (optional, will work on any Linux)
if [ -f /proc/device-tree/model ]; then
    model=$(cat /proc/device-tree/model)
    echo -e "${GREEN}Device: $model${NC}"
fi

echo -e "${YELLOW}Starting installation...${NC}"

# Update package list
echo "Updating package list..."
sudo apt-get update -qq

# Install git if not present
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    sudo apt-get install -y git -qq
fi

# Clone repository
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Project already exists. Updating...${NC}"
    cd "$INSTALL_DIR"
    git pull
else
    echo "Cloning project repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Run the full setup script
echo "Running full setup..."
cd "$INSTALL_DIR"
chmod +x quick_setup.sh
./quick_setup.sh

echo -e "${GREEN}"
echo "================================="
echo "   Installation Complete! 🎉"
echo "================================="
echo -e "${NC}"
echo
echo "To start the weather station:"
echo "  cd $INSTALL_DIR"
echo "  ./start_weather_station.sh"
echo
echo "For help, see: $INSTALL_DIR/docs/SSH_QUICK_START.md"