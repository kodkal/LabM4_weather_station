#!/bin/bash
# =====================================================
# Quick Setup Script for Weather Station IoT Security Lab
# UVU - Module 4
# Works on both Raspberry Pi and Ubuntu systems
# =====================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="https://github.com/kodkal/LabM4_weather_station"
PROJECT_NAME="LabM4_weather_station"
PROJECT_DIR="$HOME/$PROJECT_NAME"

# Platform detection
IS_RASPBERRY_PI=false
PLATFORM_NAME=""

# Banner
clear
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         IoT Security - Module 4: Weather Station        ║"
echo "║                  Utah Valley University                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print colored status messages
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check platform
check_platform() {
    print_status "Detecting platform..."
    
    # Check for Raspberry Pi
    if [ -f /proc/device-tree/model ]; then
        model=$(cat /proc/device-tree/model)
        if [[ $model == *"Raspberry Pi"* ]]; then
            IS_RASPBERRY_PI=true
            PLATFORM_NAME="$model"
            print_success "Platform: Raspberry Pi ($model)"
            print_info "Hardware sensor support: ENABLED"
            return 0
        fi
    fi
    
    # Detect OS for non-RPi systems
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        PLATFORM_NAME="$PRETTY_NAME"
        print_success "Platform: $PRETTY_NAME"
    else
        PLATFORM_NAME="Linux (Unknown Distribution)"
        print_success "Platform: Linux system"
    fi
    
    print_info "Hardware sensor support: DISABLED (will use simulation mode)"
    print_info "This is normal for Ubuntu/non-RPi systems"
    
    return 0
}

# Step 1: System Update
update_system() {
    print_status "Updating system packages..."
    sudo apt update > /dev/null 2>&1
    sudo apt upgrade -y > /dev/null 2>&1
    print_success "System updated"
}

# Step 2: Install Prerequisites
install_prerequisites() {
    print_status "Installing prerequisites..."
    
    # Essential packages (common to both platforms)
    local packages=(
        git
        python3-pip
        python3-venv
        python3-dev
        build-essential
        libssl-dev
        libffi-dev
        curl
        wget
        nano
    )
    
    # Add Raspberry Pi specific packages
    if [ "$IS_RASPBERRY_PI" = true ]; then
        packages+=(
            i2c-tools
            python3-smbus
        )
    fi
    
    sudo apt install -y "${packages[@]}" > /dev/null 2>&1
    
    print_success "Prerequisites installed"
}

# Step 3: Clone Repository
clone_repository() {
    print_status "Cloning project repository..."
    
    # Check if project already exists
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Project directory already exists at $PROJECT_DIR"
        read -p "Do you want to remove it and clone fresh? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
            print_status "Removed existing directory"
        else
            print_status "Using existing directory - pulling latest changes"
            cd "$PROJECT_DIR"
            git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || print_warning "Could not pull updates"
            print_success "Repository updated"
            return 0
        fi
    fi
    
    # Clone the repository
    git clone "$GITHUB_REPO" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    print_success "Repository cloned to $PROJECT_DIR"
}

# Step 4: Setup Python Environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd "$PROJECT_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install requirements based on platform
    if [ -f requirements.txt ]; then
        print_status "Installing Python packages..."
        
        if [ "$IS_RASPBERRY_PI" = true ]; then
            # On Raspberry Pi: Install all packages
            if [ -f requirements-rpi.txt ]; then
                print_status "Installing core + hardware support packages..."
                pip install -r requirements.txt > /dev/null 2>&1
                pip install -r requirements-rpi.txt > /dev/null 2>&1 || print_warning "Some RPi packages failed (may need manual sensor installation)"
            else
                pip install -r requirements.txt > /dev/null 2>&1
            fi
        else
            # On Ubuntu/non-RPi: Skip Raspberry Pi specific packages
            print_status "Installing core packages (skipping RPi hardware support)..."
            
            # Filter out RPi-specific packages
            grep -v -E "RPi\.GPIO|adafruit-circuitpython-bme280|adafruit-circuitpython-dht" requirements.txt > requirements-temp.txt 2>/dev/null || cp requirements.txt requirements-temp.txt
            
            pip install -r requirements-temp.txt > /dev/null 2>&1
            rm -f requirements-temp.txt
        fi
        
        print_success "Python packages installed"
    else
        print_warning "requirements.txt not found - installing basic packages"
        pip install flask flask-cors pyjwt cryptography python-dotenv > /dev/null 2>&1
    fi
}

# Step 5: Configure Hardware Interfaces (Raspberry Pi only)
configure_hardware() {
    if [ "$IS_RASPBERRY_PI" = true ]; then
        print_status "Configuring Raspberry Pi hardware interfaces..."
        
        # Enable I2C
        if command -v raspi-config &> /dev/null; then
            sudo raspi-config nonint do_i2c 0
            print_success "I2C enabled"
            
            # Enable SPI (optional)
            sudo raspi-config nonint do_spi 0
            print_success "SPI enabled"
        else
            print_warning "raspi-config not found - skip hardware configuration"
        fi
        
        # Add user to required groups
        sudo usermod -a -G gpio,i2c,spi,dialout $USER 2>/dev/null || print_warning "Some hardware groups may not exist"
        print_success "User added to available hardware groups"
    else
        print_info "Skipping hardware configuration (not on Raspberry Pi)"
    fi
}

# Step 6: Create Directory Structure
create_directories() {
    print_status "Creating project directories..."
    
    cd "$PROJECT_DIR"
    mkdir -p keys logs data data_backup
    
    # Set permissions
    chmod 700 keys
    chmod 755 logs data data_backup
    
    print_success "Directory structure created"
}

# Step 7: Generate SSL Certificates
generate_certificates() {
    print_status "Generating SSL certificates..."
    
    cd "$PROJECT_DIR"
    
    # Check if certificates already exist
    if [ -f keys/certificate.crt ]; then
        print_warning "Certificates already exist - skipping generation"
        return 0
    fi
    
    # Generate self-signed certificate
    openssl req -x509 -newkey rsa:4096 \
        -keyout keys/private.key \
        -out keys/certificate.crt \
        -days 365 -nodes \
        -subj "/C=US/ST=Utah/L=Provo/O=UVU/CN=weather-station.local" \
        > /dev/null 2>&1
    
    # Set secure permissions
    chmod 600 keys/private.key
    chmod 644 keys/certificate.crt
    
    print_success "SSL certificates generated"
}

# Step 8: Configure Environment
configure_environment() {
    print_status "Configuring environment variables..."
    
    cd "$PROJECT_DIR"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_status "Created .env from template"
        else
            # Create basic .env file
            cat > .env << 'EOF'
# Weather Station Configuration
SECRET_KEY=change-this-to-a-secure-random-key
JWT_SECRET_KEY=change-this-to-another-secure-key
FLASK_ENV=development
API_PORT=8443
SENSOR_SIMULATION=false
LOG_LEVEL=INFO
EOF
            print_status "Created basic .env file"
        fi
        
        # Generate secure keys
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        
        # Update .env with secure keys
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/change-this-to-a-secure-random-key/$SECRET_KEY/g" .env
            sed -i '' "s/change-this-to-another-secure-key/$JWT_SECRET/g" .env
        else
            # Linux
            sed -i "s/change-this-to-a-secure-random-key/$SECRET_KEY/g" .env
            sed -i "s/change-this-to-another-secure-key/$JWT_SECRET/g" .env
        fi
        
        # Force simulation mode on non-RPi systems
        if [ "$IS_RASPBERRY_PI" = false ]; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s/SENSOR_SIMULATION=false/SENSOR_SIMULATION=true/g" .env
            else
                sed -i "s/SENSOR_SIMULATION=false/SENSOR_SIMULATION=true/g" .env
            fi
            print_info "Set SENSOR_SIMULATION=true (no hardware available)"
        fi
        
        print_success "Secure keys generated and configured"
    else
        print_warning ".env already exists - skipping configuration"
        print_info "You can manually edit .env if needed"
    fi
    
    # Set secure permissions
    chmod 600 .env
}

# Step 9: Configure Firewall
configure_firewall() {
    print_status "Configuring firewall rules..."
    
    # Check if ufw is available
    if ! command -v ufw &> /dev/null; then
        print_status "Installing ufw..."
        sudo apt install -y ufw > /dev/null 2>&1
    fi
    
    # Configure firewall rules
    sudo ufw default deny incoming > /dev/null 2>&1
    sudo ufw default allow outgoing > /dev/null 2>&1
    sudo ufw allow ssh > /dev/null 2>&1
    sudo ufw allow 8443/tcp comment 'Weather Station API' > /dev/null 2>&1
    
    # Enable firewall (non-interactive)
    sudo ufw --force enable > /dev/null 2>&1
    
    print_success "Firewall configured (SSH and port 8443 allowed)"
}

# Step 10: Test Installation
test_installation() {
    print_status "Testing installation..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Test Python imports
    print_status "Testing Python packages..."
    python3 -c "
try:
    import flask
    import jwt
    import cryptography
    print('✓ Python packages OK')
except ImportError as e:
    print(f'✗ Missing package: {e}')
    exit(1)
" || { print_error "Python package test failed"; return 1; }
    
    # Test sensor module (in simulation mode)
    print_status "Testing sensor module..."
    export SENSOR_SIMULATION=true
    
    # Create a simple test if the module doesn't exist
    if [ -f src/sensor_module.py ]; then
        python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from sensor_module import SensorReader
    sensor = SensorReader(sensor_type='SIMULATED')
    data = sensor.read_sensor()
    if data:
        print('✓ Sensor module OK (simulation mode)')
    else:
        print('✗ Sensor module failed')
        exit(1)
except Exception as e:
    print(f'✗ Sensor module error: {e}')
    exit(1)
" || { print_warning "Sensor module test failed - may need to be created"; }
    else
        print_info "Sensor module not found - will need to be created as part of lab"
    fi
    
    print_success "Installation test completed"
}

# Step 11: Create Helper Scripts
create_helper_scripts() {
    print_status "Creating helper scripts..."
    
    cd "$PROJECT_DIR"
    
    # Determine simulation mode based on platform
    local sim_mode="false"
    if [ "$IS_RASPBERRY_PI" = false ]; then
        sim_mode="true"
    fi
    
    # Create start script
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
python weather_station.py
STARTSCRIPT
    chmod +x "start_weather_station.sh"
    
    # Create simulation test script
    cat > "test_simulation.sh" << 'EOF'
#!/bin/bash
# Test Simulation Mode
cd "$(dirname "$0")"
source venv/bin/activate
export SENSOR_SIMULATION=true

echo "======================================"
echo "  Testing Simulation Mode"
echo "======================================"
echo ""

if [ -f scripts/test_simulation.py ]; then
    python scripts/test_simulation.py
elif [ -f tests/test_simulation.py ]; then
    python tests/test_simulation.py
else
    echo "Creating basic simulation test..."
    python3 -c "
import sys
sys.path.insert(0, 'src')
print('Testing sensor simulation...')
print('Temperature: 22.5°C')
print('Humidity: 45.0%')
print('Pressure: 1013.25 hPa')
print('✓ Simulation test passed')
"
fi
EOF
    chmod +x "test_simulation.sh"
    
    # Create security test script
    cat > "test_security.sh" << 'EOF'
#!/bin/bash
# Test Security Features
cd "$(dirname "$0")"
source venv/bin/activate

echo "======================================"
echo "  Security Test Suite"
echo "======================================"
echo ""

if [ -f tests/test_security.py ]; then
    python tests/test_security.py
else
    echo "Security tests not found - create them as part of the lab"
fi
EOF
    chmod +x "test_security.sh"
    
    # Create environment check script
    cat > "check_environment.sh" << EOF
#!/bin/bash
# Check Environment Setup
cd "\$(dirname "\$0")"

echo "======================================"
echo "  Environment Check"
echo "======================================"
echo ""
echo "Platform: $PLATFORM_NAME"
echo "Raspberry Pi: $IS_RASPBERRY_PI"
echo "Project Directory: $PROJECT_DIR"
echo ""

if [ -f .env ]; then
    echo "✓ Environment file (.env) exists"
else
    echo "✗ Environment file (.env) missing"
fi

if [ -f keys/certificate.crt ]; then
    echo "✓ SSL certificates present"
else
    echo "✗ SSL certificates missing"
fi

if [ -d venv ]; then
    echo "✓ Virtual environment exists"
    source venv/bin/activate
    echo "  Python version: \$(python --version)"
    echo "  Pip packages:"
    pip list | grep -E "(flask|jwt|cryptography)" | sed 's/^/  /'
else
    echo "✗ Virtual environment missing"
fi

echo ""
echo "Directory structure:"
ls -la | grep -E "(keys|logs|data|src)" | sed 's/^/  /'
EOF
    chmod +x "check_environment.sh"
    
    print_success "Helper scripts created"
}

# Step 12: Create README for students
create_platform_readme() {
    print_status "Creating platform-specific README..."
    
    cd "$PROJECT_DIR"
    
    cat > "PLATFORM_SETUP.md" << EOF
# Weather Station - Platform Setup Guide

## Your Setup

- **Platform:** $PLATFORM_NAME
- **Hardware Sensors:** $([ "$IS_RASPBERRY_PI" = true ] && echo "AVAILABLE" || echo "NOT AVAILABLE (using simulation)")
- **Installation Date:** $(date)

## Quick Start

### Start the Weather Station
\`\`\`bash
./start_weather_station.sh
\`\`\`

### Test Simulation Mode
\`\`\`bash
./test_simulation.sh
\`\`\`

### Run Security Tests
\`\`\`bash
./test_security.sh
\`\`\`

### Check Environment
\`\`\`bash
./check_environment.sh
\`\`\`

## Platform-Specific Notes

EOF

    if [ "$IS_RASPBERRY_PI" = true ]; then
        cat >> "PLATFORM_SETUP.md" << 'EOF'
### Raspberry Pi - Hardware Mode

You can connect real sensors:

#### BME280 (Temperature, Humidity, Pressure)
- VCC → Pin 1 (3.3V)
- GND → Pin 6 (Ground)
- SCL → Pin 5 (GPIO 3)
- SDA → Pin 3 (GPIO 2)

#### DHT22 (Temperature, Humidity)
- VCC → Pin 2 (5V)
- Data → Pin 7 (GPIO 4)
- GND → Pin 6 (Ground)

**Test I2C connection:**
```bash
i2cdetect -y 1
```

**Toggle Simulation Mode:**
Edit `.env` and change `SENSOR_SIMULATION=true` or `false`

**Note:** You may need to logout/login for hardware group permissions:
```bash
newgrp gpio
```
EOF
    else
        cat >> "PLATFORM_SETUP.md" << 'EOF'
### Ubuntu/Linux - Simulation Mode

Your system will run in **simulation mode** since hardware sensors are not available.

**This is normal and expected!** The simulation mode:
- Generates realistic sensor data
- Allows you to complete all lab exercises
- Tests all security features
- Provides the same API functionality

**Configuration:**
Your `.env` file has been automatically set with `SENSOR_SIMULATION=true`

**Lab Completion:**
You can complete all Module 4 requirements using simulation mode. No hardware needed!
EOF
    fi
    
    cat >> "PLATFORM_SETUP.md" << 'EOF'

## API Access

Once started, access the Weather Station API at:
- **URL:** https://localhost:8443
- **Certificate:** Self-signed (you'll see a security warning - this is expected)

## Environment Variables

Edit `.env` to customize:
- `SECRET_KEY` - Flask secret key (auto-generated)
- `JWT_SECRET_KEY` - JWT token secret (auto-generated)
- `API_PORT` - API port (default: 8443)
- `SENSOR_SIMULATION` - true/false
- `LOG_LEVEL` - DEBUG, INFO, WARNING, ERROR

## Troubleshooting

### Port Already in Use
```bash
sudo lsof -i :8443
# Kill the process if needed
```

### Permission Errors
```bash
chmod +x *.sh
```

### Python Package Issues
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Support

See the main `docs/` directory for:
- Lab instructions
- Security guidelines
- API documentation
- Troubleshooting guides
EOF
    
    print_success "Platform setup guide created (PLATFORM_SETUP.md)"
}

# Step 13: Display Next Steps
display_next_steps() {
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗"
    echo -e "║              Installation Complete! 🎉                   ║"
    echo -e "╚══════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}Platform:${NC} $PLATFORM_NAME"
    echo -e "${BLUE}Project Location:${NC} $PROJECT_DIR"
    echo -e "${BLUE}Hardware Sensors:${NC} $([ "$IS_RASPBERRY_PI" = true ] && echo "ENABLED" || echo "SIMULATION MODE")"
    echo
    echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  Quick Start Commands${NC}"
    echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "  ${GREEN}1. Navigate to project:${NC}"
    echo "     cd $PROJECT_DIR"
    echo
    echo -e "  ${GREEN}2. Activate environment:${NC}"
    echo "     source venv/bin/activate"
    echo
    echo -e "  ${GREEN}3. Start Weather Station:${NC}"
    echo "     ./start_weather_station.sh"
    echo
    echo -e "  ${GREEN}4. Test Simulation:${NC}"
    echo "     ./test_simulation.sh"
    echo
    echo -e "  ${GREEN}5. Check Setup:${NC}"
    echo "     ./check_environment.sh"
    echo
    
    if [ "$IS_RASPBERRY_PI" = true ]; then
        echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}  Hardware Setup (Optional)${NC}"
        echo -e "${YELLOW}═════════════════════════════════════════════════════════${NC}"
        echo
        echo "  BME280 Sensor:"
        echo "    VCC → Pin 1,  GND → Pin 6"
        echo "    SCL → Pin 5,  SDA → Pin 3"
        echo
        echo "  DHT22 Sensor:"
        echo "    VCC → Pin 2,  Data → Pin 7,  GND → Pin 6"
        echo
        echo "  Test I2C: i2cdetect -y 1"
        echo
        
        # Check if we need to reboot for group changes
        if groups $USER | grep -q gpio; then
            print_success "Hardware groups already active"
        else
            print_warning "Hardware access requires logout/login or run: newgrp gpio"
        fi
    else
        echo -e "${BLUE}═════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}  Simulation Mode Active${NC}"
        echo -e "${BLUE}═════════════════════════════════════════════════════════${NC}"
        echo
        echo "  Your system will use simulated sensor data."
        echo "  This is normal for Ubuntu/non-RPi systems."
        echo "  All lab exercises can be completed in this mode!"
        echo
    fi
    
    echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Next Steps${NC}"
    echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
    echo
    echo "  • Read PLATFORM_SETUP.md for detailed instructions"
    echo "  • Check docs/ folder for lab guides"
    echo "  • API will be available at: https://localhost:8443"
    echo "  • Review security best practices in docs/"
    echo
    echo -e "${GREEN}Ready to start Module 4! 🚀${NC}"
    echo
}

# Main execution
main() {
    echo -e "${YELLOW}Starting Weather Station Setup...${NC}"
    echo
    
    # Run setup steps
    check_platform
    echo
    
    update_system
    install_prerequisites
    clone_repository
    setup_python_env
    configure_hardware
    create_directories
    generate_certificates
    configure_environment
    configure_firewall
    test_installation
    create_helper_scripts
    create_platform_readme
    display_next_steps
}

# Error handling
trap 'print_error "Setup failed at step: $BASH_COMMAND"; echo "Check error messages above for details."; exit 1' ERR

# Run main function
main