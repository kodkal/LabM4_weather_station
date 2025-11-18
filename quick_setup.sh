#!/bin/bash
# =====================================================
# Quick Setup Script for Weather Station IoT Security Lab
# UVU - Module 4
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

# Banner
clear
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         IoT Security - Module 4: Weather Station        ║"
echo "║                  Utah Valley University                 ║"
echo "╔══════════════════════════════════════════════════════════╗"
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

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if [ -f /proc/device-tree/model ]; then
        model=$(cat /proc/device-tree/model)
        if [[ $model == *"Raspberry Pi"* ]]; then
            print_success "Running on Raspberry Pi: $model"
            return 0
        fi
    fi
    print_warning "Not running on Raspberry Pi - some features may not work"
    return 1
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
    
    # Essential packages
    sudo apt install -y \
        git \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libssl-dev \
        libffi-dev \
        i2c-tools \
        python3-smbus \
        curl \
        wget \
        nano \
        > /dev/null 2>&1
    
    print_success "Prerequisites installed"
}

# Step 3: Clone Repository
clone_repository() {
    print_status "Cloning project repository..."
    
    # Check if project already exists
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Project directory already exists"
        read -p "Do you want to remove it and clone fresh? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
            print_status "Removed existing directory"
        else
            print_status "Using existing directory"
            cd "$PROJECT_DIR"
            git pull origin main
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
    
    # Install requirements
    if [ -f requirements.txt ]; then
        print_status "Installing Python packages..."
        pip install -r requirements.txt > /dev/null 2>&1
        print_success "Python packages installed"
    else
        print_warning "requirements.txt not found - skipping package installation"
    fi
}

# Step 5: Configure Hardware Interfaces
configure_hardware() {
    if check_raspberry_pi; then
        print_status "Configuring hardware interfaces..."
        
        # Enable I2C
        sudo raspi-config nonint do_i2c 0
        print_success "I2C enabled"
        
        # Enable SPI (optional)
        sudo raspi-config nonint do_spi 0
        print_success "SPI enabled"
        
        # Add user to required groups
        sudo usermod -a -G gpio,i2c,spi,dialout $USER
        print_success "User added to hardware groups"
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
        print_warning "Certificates already exist"
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
    print_status "Configuring environment..."
    
    cd "$PROJECT_DIR"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_status "Created .env from template"
            
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
            
            print_success "Secure keys generated and configured"
        else
            print_warning ".env.example not found - manual configuration required"
        fi
    else
        print_warning ".env already exists - skipping configuration"
    fi
    
    # Set secure permissions
    chmod 600 .env
}

# Step 9: Configure Firewall
configure_firewall() {
    if check_raspberry_pi; then
        print_status "Configuring firewall..."
        
        # Install ufw if not present
        if ! command -v ufw &> /dev/null; then
            sudo apt install -y ufw > /dev/null 2>&1
        fi
        
        # Configure firewall rules
        sudo ufw default deny incoming > /dev/null 2>&1
        sudo ufw default allow outgoing > /dev/null 2>&1
        sudo ufw allow ssh > /dev/null 2>&1
        sudo ufw allow 8443/tcp comment 'Weather Station API' > /dev/null 2>&1
        
        # Enable firewall (non-interactive)
        sudo ufw --force enable > /dev/null 2>&1
        
        print_success "Firewall configured"
    fi
}

# Step 10: Test Installation
test_installation() {
    print_status "Testing installation..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Test Python imports
    python3 -c "
try:
    import flask
    import jwt
    import cryptography
    print('✓ Python packages OK')
except ImportError as e:
    print(f'✗ Missing package: {e}')
    exit(1)
" || return 1
    
    # Test sensor module (in simulation mode)
    export SENSOR_SIMULATION=true
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
" || return 1
    
    print_success "Installation test passed"
}

# Step 11: Create Desktop Shortcuts
create_shortcuts() {
    print_status "Creating shortcuts..."
    
    # Create start script
    cat > "$PROJECT_DIR/start_weather_station.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting Weather Station..."
echo "Access the API at: https://localhost:8443"
echo "Press Ctrl+C to stop"
python src/weather_station.py
EOF
    chmod +x "$PROJECT_DIR/start_weather_station.sh"
    
    # Create simulation test script
    cat > "$PROJECT_DIR/test_simulation.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export SENSOR_SIMULATION=true
python scripts/test_simulation.py
EOF
    chmod +x "$PROJECT_DIR/test_simulation.sh"
    
    # Create security test script
    cat > "$PROJECT_DIR/test_security.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python tests/test_security.py
EOF
    chmod +x "$PROJECT_DIR/test_security.sh"
    
    print_success "Shortcuts created"
}

# Step 12: Display Next Steps
display_next_steps() {
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗"
    echo -e "║              Installation Complete! 🎉                   ║"
    echo -e "╚══════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}Project Location:${NC} $PROJECT_DIR"
    echo
    echo -e "${YELLOW}Quick Start Commands:${NC}"
    echo "  cd $PROJECT_DIR"
    echo "  source venv/bin/activate"
    echo
    echo -e "${YELLOW}Run Weather Station:${NC}"
    echo "  ./start_weather_station.sh"
    echo
    echo -e "${YELLOW}Test Simulation Mode:${NC}"
    echo "  ./test_simulation.sh"
    echo
    echo -e "${YELLOW}Run Security Tests:${NC}"
    echo "  ./test_security.sh"
    echo
    echo -e "${YELLOW}Connect Sensor (Optional):${NC}"
    echo "  BME280: VCC→Pin1, GND→Pin6, SCL→Pin5, SDA→Pin3"
    echo "  DHT22:  VCC→Pin2, Data→Pin7, GND→Pin6"
    echo
    echo -e "${GREEN}Ready to start the lab! Check the docs/ folder for guides.${NC}"
    echo
    
    # Check if we need to reboot for group changes
    if groups $USER | grep -q gpio; then
        print_success "Hardware groups already active"
    else
        print_warning "You may need to logout and login again for hardware access"
        print_warning "Or run: newgrp gpio"
    fi
}

# Main execution
main() {
    echo -e "${YELLOW}Starting Weather Station Setup...${NC}"
    echo
    
    # Run setup steps
    check_raspberry_pi
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
    create_shortcuts
    display_next_steps
}

# Error handling
trap 'print_error "Setup failed! Check the error messages above."; exit 1' ERR

# Run main function
main