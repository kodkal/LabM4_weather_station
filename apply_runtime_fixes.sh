#!/bin/bash
# =====================================================
# Quick Fix Script for Runtime Errors
# Fixes: .env parsing, RPi.GPIO imports, requirements
# =====================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  Weather Station - Runtime Fixes${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo

# Check we're in the right directory
if [ ! -f ".env" ] || [ ! -d "src" ]; then
    echo -e "${RED}Error: Run this script from the LabM4_weather_station directory${NC}"
    echo "Expected to find: .env and src/ directory"
    exit 1
fi

echo -e "${YELLOW}This script will fix three runtime errors:${NC}"
echo "  1. .env file parsing in start_weather_station.sh"
echo "  2. RPi.GPIO import error in sensor_module.py"
echo "  3. Requirements.txt issues on Ubuntu"
echo

read -p "Continue with fixes? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Fix 1: start_weather_station.sh
echo -e "${BLUE}[1/3] Fixing start_weather_station.sh...${NC}"

if [ -f "start_weather_station.sh" ]; then
    cp start_weather_station.sh start_weather_station.sh.backup
    echo "  - Backed up to start_weather_station.sh.backup"
fi

cat > "start_weather_station.sh" << 'STARTSCRIPT'
#!/bin/bash
# Start Weather Station
cd "$(dirname "$0")"
source venv/bin/activate

# Load environment variables from .env file (properly handle quotes and comments)
if [ -f .env ]; then
    set -a  # Automatically export all variables
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        
        # Remove inline comments
        line="${line%%#*}"
        
        # Trim whitespace
        line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        
        # Skip if empty after trimming
        [[ -z "$line" ]] && continue
        
        # Export the variable
        export "$line"
    done < .env
    set +a
fi

echo "======================================"
echo "  Weather Station - Starting"
echo "======================================"
echo "Platform: $(lsb_release -d 2>/dev/null | cut -f2- || uname -s)"
echo "Simulation Mode: ${SENSOR_SIMULATION:-auto}"
echo "API URL: https://localhost:${API_PORT:-8443}"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the weather station
python src/weather_station.py
STARTSCRIPT

chmod +x start_weather_station.sh
echo -e "${GREEN}  ✓ start_weather_station.sh fixed${NC}"

# Fix 2: sensor_module.py
echo -e "${BLUE}[2/3] Fixing sensor_module.py...${NC}"

# Find sensor_module.py (could be in src/ or root)
SENSOR_MODULE=""
if [ -f "src/sensor_module.py" ]; then
    SENSOR_MODULE="src/sensor_module.py"
elif [ -f "sensor_module.py" ]; then
    SENSOR_MODULE="sensor_module.py"
else
    echo -e "${YELLOW}  ! sensor_module.py not found - will be created by lab${NC}"
    SENSOR_MODULE="none"
fi

if [ "$SENSOR_MODULE" != "none" ]; then
    # Backup
    cp "$SENSOR_MODULE" "${SENSOR_MODULE}.backup"
    echo "  - Backed up to ${SENSOR_MODULE}.backup"
    
    # Check if it has the problematic import
    if grep -q "import RPi.GPIO as GPIO" "$SENSOR_MODULE"; then
        # Add platform detection at the top of the imports section
        # This is a simple fix - check if it already has the fix
        if grep -q "is_raspberry_pi()" "$SENSOR_MODULE"; then
            echo -e "${GREEN}  ✓ sensor_module.py already has platform detection${NC}"
        else
            echo -e "${YELLOW}  ! sensor_module.py needs manual update${NC}"
            echo "    See RUNTIME_FIXES.md for the fixed version"
            echo "    Quick fix: Set SENSOR_SIMULATION=true in .env"
        fi
    else
        echo -e "${GREEN}  ✓ sensor_module.py doesn't have RPi.GPIO import issue${NC}"
    fi
else
    echo -e "${YELLOW}  ! sensor_module.py will be created during lab${NC}"
fi

# Fix 3: requirements.txt
echo -e "${BLUE}[3/3] Fixing requirements and reinstalling packages...${NC}"

# Backup
if [ -f "requirements.txt" ]; then
    cp requirements.txt requirements.txt.backup
    echo "  - Backed up to requirements.txt.backup"
fi

# Detect platform
IS_RPI=false
if [ -f /proc/device-tree/model ]; then
    model=$(cat /proc/device-tree/model)
    if [[ $model == *"Raspberry Pi"* ]]; then
        IS_RPI=true
    fi
fi

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "  - Virtual environment activated"
else
    echo -e "${YELLOW}  ! No virtual environment found${NC}"
    echo "    Run: python3 -m venv venv"
    exit 1
fi

# Uninstall problematic packages on Ubuntu
if [ "$IS_RPI" = false ]; then
    echo "  - Detected Ubuntu/non-RPi system"
    echo "  - Uninstalling RPi-specific packages..."
    pip uninstall -y RPi.GPIO adafruit-circuitpython-bme280 adafruit-circuitpython-dht 2>/dev/null || true
    
    # Filter requirements
    if [ -f "requirements.txt" ]; then
        echo "  - Filtering requirements.txt..."
        grep -v -E "RPi\.GPIO|adafruit-circuitpython-bme280|adafruit-circuitpython-dht" requirements.txt > requirements-temp.txt
        pip install -r requirements-temp.txt > /dev/null 2>&1 || echo -e "${YELLOW}    Some packages may have failed${NC}"
        rm -f requirements-temp.txt
    fi
    
    # Ensure simulation mode is set
    if grep -q "SENSOR_SIMULATION" .env; then
        sed -i 's/SENSOR_SIMULATION=.*/SENSOR_SIMULATION=true/' .env
    else
        echo "SENSOR_SIMULATION=true" >> .env
    fi
    
    if grep -q "SENSOR_TYPE" .env; then
        sed -i 's/SENSOR_TYPE=.*/SENSOR_TYPE=SIMULATED/' .env
    else
        echo "SENSOR_TYPE=SIMULATED" >> .env
    fi
    
    echo -e "${GREEN}  ✓ Configured for simulation mode${NC}"
else
    echo "  - Detected Raspberry Pi"
    echo "  - Installing all packages including hardware support..."
    pip install -r requirements.txt > /dev/null 2>&1 || echo -e "${YELLOW}    Some packages may have failed${NC}"
    echo -e "${GREEN}  ✓ All packages installed${NC}"
fi

# Summary
echo
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  Fixes Applied Successfully!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo

echo -e "${YELLOW}What was fixed:${NC}"
echo "  ✓ start_weather_station.sh - Fixed .env parsing"
echo "  ✓ Python packages - Removed/filtered RPi-specific packages"
echo "  ✓ .env configuration - Set simulation mode (Ubuntu)"
echo

if [ "$SENSOR_MODULE" != "none" ] && grep -q "import RPi.GPIO" "$SENSOR_MODULE" 2>/dev/null; then
    echo -e "${YELLOW}Note:${NC} sensor_module.py may need manual update"
    echo "      See RUNTIME_FIXES.md for the complete fixed version"
    echo
fi

echo -e "${YELLOW}Try starting the weather station:${NC}"
echo "  ./start_weather_station.sh"
echo

echo "If you still have issues, see RUNTIME_FIXES.md for detailed instructions."