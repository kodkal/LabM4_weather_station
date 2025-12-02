#!/bin/bash
# =====================================================
# Student Onboarding Script
# Personalized setup for each student
# =====================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
PROJECT_DIR="$HOME/LabM4_weather_station"

# Banner
clear
echo -e "${CYAN}"
cat << "EOF"
 _       __           __  __              _____ __        __  _           
| |     / /__  ____ _/ /_/ /_  ___  _____/ ___// /_____ _/ /_(_)___  ____ 
| | /| / / _ \/ __ `/ __/ __ \/ _ \/ ___/\__ \/ __/ __ `/ __/ / __ \/ __ \
| |/ |/ /  __/ /_/ / /_/ / / /  __/ /   ___/ / /_/ /_/ / /_/ / /_/ / / / /
|__/|__/\___/\__,_/\__/_/ /_/\___/_/   /____/\__/\__,_/\__/_/\____/_/ /_/ 
                                                                           
                    IoT Security Lab - Module 4
                      Utah Valley University
EOF
echo -e "${NC}"

# Detect platform from PLATFORM_SETUP.md if available
IS_RASPBERRY_PI=false
PLATFORM_NAME="Unknown"

if [ -f "$PROJECT_DIR/PLATFORM_SETUP.md" ]; then
    # Extract platform info from the generated file
    PLATFORM_LINE=$(grep "^- \*\*Platform:\*\*" "$PROJECT_DIR/PLATFORM_SETUP.md" 2>/dev/null | head -1)
    if [[ $PLATFORM_LINE == *"Raspberry Pi"* ]]; then
        IS_RASPBERRY_PI=true
        PLATFORM_NAME=$(echo "$PLATFORM_LINE" | sed 's/.*Platform:\*\* //' | sed 's/$//')
    else
        PLATFORM_NAME=$(echo "$PLATFORM_LINE" | sed 's/.*Platform:\*\* //' | sed 's/$//')
    fi
fi

# Fallback: detect directly
if [ "$PLATFORM_NAME" == "Unknown" ]; then
    if [ -f /proc/device-tree/model ]; then
        model=$(cat /proc/device-tree/model)
        if [[ $model == *"Raspberry Pi"* ]]; then
            IS_RASPBERRY_PI=true
            PLATFORM_NAME="$model"
        fi
    fi
    
    if [ "$PLATFORM_NAME" == "Unknown" ] && [ -f /etc/os-release ]; then
        . /etc/os-release
        PLATFORM_NAME="$PRETTY_NAME"
    fi
fi

# Welcome message
echo -e "${YELLOW}Welcome to the Weather Station Security Lab!${NC}"
echo
echo -e "${BLUE}Detected Platform:${NC} $PLATFORM_NAME"
if [ "$IS_RASPBERRY_PI" = true ]; then
    echo -e "${GREEN}Hardware sensors available${NC}"
else
    echo -e "${CYAN}Simulation mode (no hardware needed)${NC}"
fi
echo
echo "Let's personalize your setup..."
echo

# Get student information
read -p "Enter your name (for identification): " STUDENT_NAME
STUDENT_NAME=${STUDENT_NAME:-"Student"}

# Get student ID (optional)
read -p "Enter your student ID (optional, press Enter to skip): " STUDENT_ID

# Choose experience level
echo
echo "Select your experience level:"
echo "  1) Beginner - New to IoT/Security"
echo "  2) Intermediate - Some programming experience"
echo "  3) Advanced - Comfortable with security concepts"
read -p "Enter choice [1-3]: " LEVEL

case $LEVEL in
    1) LEVEL_NAME="Beginner" ;;
    2) LEVEL_NAME="Intermediate" ;;
    3) LEVEL_NAME="Advanced" ;;
    *) LEVEL_NAME="Intermediate" ;;
esac

# Sensor mode selection - only ask if on Raspberry Pi
if [ "$IS_RASPBERRY_PI" = true ]; then
    echo
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  You have a Raspberry Pi! Hardware sensors are available.${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo
    echo "How do you want to run the lab?"
    echo
    echo -e "  ${CYAN}1)${NC} Simulation Mode ${YELLOW}(no sensors needed - recommended to start)${NC}"
    echo -e "  ${CYAN}2)${NC} Hardware Mode - BME280 sensor ${BLUE}(I2C: temp/humidity/pressure)${NC}"
    echo -e "  ${CYAN}3)${NC} Hardware Mode - DHT22 sensor ${BLUE}(GPIO: temp/humidity only)${NC}"
    echo -e "  ${CYAN}4)${NC} Hardware Mode - AHT20+BMP280 combo ${BLUE}(I2C: temp/humidity/pressure)${NC}"
    echo -e "  ${CYAN}5)${NC} Auto-detect hardware, fallback to simulation if not found"
    echo
    read -p "Enter choice [1-5]: " MODE
    
    case $MODE in
        1) 
            SENSOR_MODE="SIMULATED"
            MODE_NAME="Simulation"
            USE_SIMULATION=true
            SENSOR_DESCRIPTION="Simulated sensor data"
            USE_I2C=false
            ;;
        2) 
            SENSOR_MODE="BME280"
            MODE_NAME="Hardware (BME280)"
            USE_SIMULATION=false
            SENSOR_DESCRIPTION="BME280 - I2C Temperature/Humidity/Pressure sensor"
            USE_I2C=true
            ;;
        3) 
            SENSOR_MODE="DHT22"
            MODE_NAME="Hardware (DHT22)"
            USE_SIMULATION=false
            SENSOR_DESCRIPTION="DHT22 - GPIO Temperature/Humidity sensor"
            USE_I2C=false
            ;;
        4) 
            SENSOR_MODE="AHT20BMP280"
            MODE_NAME="Hardware (AHT20+BMP280)"
            USE_SIMULATION=false
            SENSOR_DESCRIPTION="AHT20+BMP280 combo - I2C Temperature/Humidity/Pressure sensor"
            USE_I2C=true
            
            # Check if the AHT20+BMP280 module exists
            if [ ! -f "$PROJECT_DIR/aht20_bmp280_sensor.py" ]; then
                echo
                echo -e "${YELLOW}[!] AHT20+BMP280 sensor module not found.${NC}"
                echo -e "${BLUE}[*] The module needs to be installed for this sensor to work.${NC}"
                echo
                echo "You have two options:"
                echo "  a) Download from course materials"
                echo "  b) Continue anyway (will need to add module later)"
                echo
                read -p "Continue with setup? (y/n): " CONTINUE_AHT
                if [[ ! $CONTINUE_AHT =~ ^[Yy]$ ]]; then
                    echo "Setup cancelled. Please obtain the aht20_bmp280_sensor.py module first."
                    exit 1
                fi
            fi
            ;;
        5) 
            SENSOR_MODE="AUTO"
            MODE_NAME="Auto-detect"
            USE_SIMULATION=false
            SENSOR_DESCRIPTION="Will try to detect connected hardware sensors"
            USE_I2C=true
            ;;
        *) 
            SENSOR_MODE="SIMULATED"
            MODE_NAME="Simulation"
            USE_SIMULATION=true
            SENSOR_DESCRIPTION="Simulated sensor data"
            USE_I2C=false
            ;;
    esac
    
    # Show sensor wiring info for hardware modes
    if [ "$USE_SIMULATION" = false ]; then
        echo
        echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}  Sensor Wiring Reference${NC}"
        echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
        
        case $SENSOR_MODE in
            "BME280"|"AHT20BMP280")
                echo
                echo "  I2C Connection (BME280 / AHT20+BMP280):"
                echo "  ┌─────────────┬──────────────────┐"
                echo "  │ Sensor Pin  │ Raspberry Pi Pin │"
                echo "  ├─────────────┼──────────────────┤"
                echo "  │ VCC         │ Pin 1 (3.3V)     │"
                echo "  │ GND         │ Pin 6 (Ground)   │"
                echo "  │ SCL         │ Pin 5 (GPIO3)    │"
                echo "  │ SDA         │ Pin 3 (GPIO2)    │"
                echo "  └─────────────┴──────────────────┘"
                echo
                if [ "$SENSOR_MODE" = "AHT20BMP280" ]; then
                    echo "  AHT20 I2C Address: 0x38"
                    echo "  BMP280 I2C Address: 0x76 or 0x77"
                else
                    echo "  BME280 I2C Address: 0x76 or 0x77"
                fi
                echo
                echo "  Test I2C connection: i2cdetect -y 1"
                ;;
            "DHT22")
                echo
                echo "  GPIO Connection (DHT22):"
                echo "  ┌─────────────┬──────────────────┐"
                echo "  │ Sensor Pin  │ Raspberry Pi Pin │"
                echo "  ├─────────────┼──────────────────┤"
                echo "  │ VCC         │ Pin 2 (5V)       │"
                echo "  │ Data        │ Pin 7 (GPIO4)    │"
                echo "  │ GND         │ Pin 6 (Ground)   │"
                echo "  └─────────────┴──────────────────┘"
                echo
                echo "  Note: Some DHT22 modules need a pull-up resistor"
                ;;
            "AUTO")
                echo
                echo "  Auto-detect will try sensors in this order:"
                echo "    1. AHT20+BMP280 (I2C 0x38 + 0x76/0x77)"
                echo "    2. BME280 (I2C 0x76/0x77)"
                echo "    3. DHT22 (GPIO4)"
                echo "    4. Simulation mode (fallback)"
                ;;
        esac
        echo
    fi
else
    # Ubuntu/non-RPi - automatically use simulation
    echo
    echo -e "${CYAN}Your system will use Simulation Mode${NC}"
    echo "This is automatic because you don't have Raspberry Pi hardware."
    echo "You'll still complete all lab objectives!"
    
    SENSOR_MODE="SIMULATED"
    MODE_NAME="Simulation"
    USE_SIMULATION=true
    SENSOR_DESCRIPTION="Simulated sensor data"
    USE_I2C=false
fi

# =====================================================
# COMMON DEPENDENCIES (All platforms)
# =====================================================
echo
echo -e "${BLUE}[*] Installing common Python dependencies...${NC}"

cd "$PROJECT_DIR"

# Create/activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${CYAN}    Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi
source venv/bin/activate

# Upgrade pip silently
pip install --upgrade pip > /dev/null 2>&1

# Install colorama (needed for test_security.py)
echo -e "${CYAN}    Installing colorama (for security tests)...${NC}"
pip install colorama > /dev/null 2>&1
echo -e "${GREEN}    ✅ colorama installed${NC}"

# Install pyyaml
echo -e "${CYAN}    Installing pyyaml...${NC}"
pip install pyyaml > /dev/null 2>&1
echo -e "${GREEN}    ✅ pyyaml installed${NC}"

# Install requirements.txt if it exists
if [ -f requirements.txt ]; then
    echo -e "${CYAN}    Installing requirements from requirements.txt...${NC}"
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}    ✅ Requirements installed${NC}"
fi

# =====================================================
# HARDWARE DEPENDENCIES SETUP (Raspberry Pi only)
# =====================================================
if [ "$IS_RASPBERRY_PI" = true ] && [ "$USE_SIMULATION" = false ]; then
    echo
    echo -e "${MAGENTA}════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  Installing Hardware Dependencies${NC}"
    echo -e "${MAGENTA}════════════════════════════════════════════════════════════${NC}"
    echo
    
    # Ensure we're in the project directory and venv is active
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Install I2C dependencies for I2C sensors
    if [ "$USE_I2C" = true ]; then
        echo -e "${BLUE}[*] Installing I2C dependencies (smbus, smbus2)...${NC}"
        pip install smbus smbus2 2>/dev/null || {
            echo -e "${YELLOW}    Installing smbus via apt...${NC}"
            sudo apt-get update -qq
            sudo apt-get install -y python3-smbus i2c-tools > /dev/null 2>&1
            pip install smbus2 2>/dev/null || true
        }
        echo -e "${GREEN}    ✅ I2C libraries installed${NC}"
        
        # Verify I2C is enabled
        echo
        echo -e "${BLUE}[*] Checking I2C interface...${NC}"
        if [ -e /dev/i2c-1 ]; then
            echo -e "${GREEN}    ✅ I2C interface is enabled (/dev/i2c-1)${NC}"
            
            # Run i2cdetect to show connected devices
            echo
            echo -e "${CYAN}[*] Scanning I2C bus for connected devices...${NC}"
            echo
            sudo i2cdetect -y 1 2>/dev/null || {
                echo -e "${YELLOW}    ⚠️  Could not scan I2C bus (may need permissions)${NC}"
                echo "    Try running: sudo i2cdetect -y 1"
            }
            echo
            
            # Expected addresses based on sensor type
            case $SENSOR_MODE in
                "AHT20BMP280")
                    echo -e "${CYAN}    Expected addresses:${NC}"
                    echo "      • 0x38 = AHT20 (temperature/humidity)"
                    echo "      • 0x76 or 0x77 = BMP280 (pressure)"
                    ;;
                "BME280")
                    echo -e "${CYAN}    Expected addresses:${NC}"
                    echo "      • 0x76 or 0x77 = BME280"
                    ;;
            esac
        else
            echo -e "${YELLOW}    ⚠️  I2C interface not enabled!${NC}"
            echo
            echo -e "${YELLOW}    To enable I2C:${NC}"
            echo "      1. Run: sudo raspi-config"
            echo "      2. Go to: Interface Options → I2C → Enable"
            echo "      3. Reboot your Pi"
            echo
            read -p "    Continue anyway? (y/n): " CONTINUE_I2C
            if [[ ! $CONTINUE_I2C =~ ^[Yy]$ ]]; then
                echo "    Please enable I2C and run this script again."
                exit 1
            fi
        fi
    fi
    
    # Firewall setup
    echo
    echo -e "${BLUE}[*] Configuring firewall (UFW)...${NC}"
    
    # Check if ufw is installed
    if ! command -v ufw &> /dev/null; then
        echo -e "${YELLOW}    Installing UFW...${NC}"
        sudo apt-get update -qq
        sudo apt-get install -y ufw > /dev/null 2>&1
    fi
    
    # Allow the weather station port
    echo -e "${CYAN}    Allowing port 8080/tcp for Weather Station API...${NC}"
    sudo ufw allow 8080/tcp > /dev/null 2>&1 || true
    
    # Allow HTTPS port as well
    echo -e "${CYAN}    Allowing port 8443/tcp for HTTPS API...${NC}"
    sudo ufw allow 8443/tcp > /dev/null 2>&1 || true
    
    # Check if UFW is enabled
    UFW_STATUS=$(sudo ufw status 2>/dev/null | head -1)
    if [[ $UFW_STATUS == *"inactive"* ]]; then
        echo -e "${YELLOW}    ⚠️  UFW is installed but not enabled${NC}"
        echo "    To enable: sudo ufw enable"
        echo "    (SSH access on port 22 should be allowed first!)"
    else
        echo -e "${GREEN}    ✅ Firewall rules configured${NC}"
    fi
    
    # Test sensor if applicable
    echo
    echo -e "${BLUE}[*] Testing sensor connection...${NC}"
    
    case $SENSOR_MODE in
        "AHT20BMP280")
            if [ -f "aht20_bmp280_sensor.py" ]; then
                echo -e "${CYAN}    Running AHT20+BMP280 sensor test...${NC}"
                python3 aht20_bmp280_sensor.py 2>&1 | head -10 || {
                    echo -e "${YELLOW}    ⚠️  Sensor test had issues${NC}"
                    echo "    This may be normal if sensor isn't connected yet."
                }
            else
                echo -e "${YELLOW}    ⚠️  aht20_bmp280_sensor.py not found${NC}"
                echo "    You'll need to add this file for hardware mode to work."
            fi
            ;;
        "BME280")
            echo -e "${CYAN}    BME280 sensor will be tested when starting the weather station${NC}"
            ;;
        "DHT22")
            echo -e "${CYAN}    DHT22 sensor will be tested when starting the weather station${NC}"
            ;;
        "AUTO")
            echo -e "${CYAN}    Sensors will be auto-detected when starting the weather station${NC}"
            ;;
    esac
    
    echo
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Hardware Dependencies Setup Complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo
fi

# Create student profile
echo
echo -e "${BLUE}Creating your profile...${NC}"

# Create student profile file
cat > .student_profile << EOF
# Student Profile - Weather Station Lab
STUDENT_NAME="$STUDENT_NAME"
STUDENT_ID="$STUDENT_ID"
LEVEL="$LEVEL_NAME"
MODE="$MODE_NAME"
PLATFORM="$PLATFORM_NAME"
IS_RASPBERRY_PI="$IS_RASPBERRY_PI"
START_DATE="$(date)"
SENSOR_TYPE="$SENSOR_MODE"
SENSOR_DESCRIPTION="$SENSOR_DESCRIPTION"
EOF

# Update .env with student settings
if [ -f .env ]; then
    # Update sensor type
    if grep -q "^SENSOR_TYPE=" .env; then
        sed -i "s/SENSOR_TYPE=.*/SENSOR_TYPE=$SENSOR_MODE/" .env
    else
        echo "SENSOR_TYPE=$SENSOR_MODE" >> .env
    fi
    
    # Set simulation flag if needed
    if [ "$USE_SIMULATION" = true ]; then
        sed -i "s/SENSOR_SIMULATION=.*/SENSOR_SIMULATION=true/" .env
    else
        sed -i "s/SENSOR_SIMULATION=.*/SENSOR_SIMULATION=false/" .env
    fi
    
    # Set device ID with student identifier
    DEVICE_ID="weather-$(echo $STUDENT_NAME | tr ' ' '-' | tr '[:upper:]' '[:lower:]')-$(date +%s | tail -c 5)"
    if grep -q "^DEVICE_ID=" .env; then
        sed -i "s/DEVICE_ID=.*/DEVICE_ID=$DEVICE_ID/" .env
    else
        echo "DEVICE_ID=$DEVICE_ID" >> .env
    fi
fi

# Create personalized workspace
echo -e "${BLUE}Setting up your workspace...${NC}"

# Create student work directory
mkdir -p student_work
cat > student_work/README.md << EOF
# $STUDENT_NAME's Work Directory

This is your personal workspace for the Weather Station Lab.
- Save your modified code here
- Document your findings
- Keep your test results

**Student:** $STUDENT_NAME
**Level:** $LEVEL_NAME
**Mode:** $MODE_NAME
**Sensor:** $SENSOR_DESCRIPTION
**Platform:** $PLATFORM_NAME
**Started:** $(date)
EOF

# Generate quick reference card
cat > student_work/quick_reference.txt << EOF
========================================
 QUICK REFERENCE - $STUDENT_NAME
========================================

YOUR SETTINGS:
- Platform: $PLATFORM_NAME
- Mode: $MODE_NAME
- Sensor: $SENSOR_MODE
- Level: $LEVEL_NAME
- Device ID: $DEVICE_ID

QUICK COMMANDS:
--------------
Start Weather Station:
  ./start_weather_station.sh

Test Simulation:
  ./test_simulation.sh

Run Security Tests:
  ./test_security.sh

Check Your Setup:
  ./check_environment.sh

Activate Python Environment:
  source venv/bin/activate

View Your Profile:
  cat .student_profile

Test I2C Sensors (if using hardware):
  i2cdetect -y 1

IMPORTANT FILES:
---------------
Main Code: weather_station.py
Sensor Module: sensor_module.py
$([ "$SENSOR_MODE" = "AHT20BMP280" ] && echo "AHT20+BMP280: aht20_bmp280_sensor.py")
Your Work: student_work/
Config: .env
Logs: logs/weather_station.log
Platform Guide: PLATFORM_SETUP.md

API ACCESS:
----------
URL: https://localhost:8443
Default credentials (CHANGE THESE!):
  Username: admin
  Password: admin123

SENSOR INFO ($SENSOR_MODE):
--------------------------
$SENSOR_DESCRIPTION
$([ "$USE_SIMULATION" = false ] && echo "
Hardware Tips:
- Check connections if readings fail
- Use i2cdetect -y 1 for I2C sensors
- Verify permissions: groups \$USER")

HARDWARE TROUBLESHOOTING:
------------------------
If you see 'No module named smbus':
  source venv/bin/activate
  pip install smbus smbus2

If I2C not detected:
  sudo raspi-config → Interface Options → I2C → Enable
  sudo reboot

Test I2C devices:
  sudo i2cdetect -y 1

Test AHT20+BMP280 sensor:
  python3 aht20_bmp280_sensor.py

HELP:
----
Platform Info: PLATFORM_SETUP.md
Student Guide: docs/STUDENT_GUIDE.md
$([ "$IS_RASPBERRY_PI" = false ] && echo "Simulation Guide: docs/SIMULATION_GUIDE.md")

========================================
EOF

# Set up level-appropriate configurations
echo -e "${BLUE}Configuring for $LEVEL_NAME level...${NC}"

case $LEVEL in
    1)  # Beginner
        # Enable more logging
        if [ -f .env ]; then
            sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=DEBUG/" .env 2>/dev/null || true
            if grep -q "^DEBUG=" .env; then
                sed -i "s/DEBUG=.*/DEBUG=True/" .env 2>/dev/null || true
            else
                echo "DEBUG=True" >> .env
            fi
        fi
        
        # Create beginner hints file
        cat > student_work/hints.txt << EOF
BEGINNER HINTS - Getting Started:
=================================

STEP 1: UNDERSTAND THE SYSTEM
-----------------------------
1. Start the weather station: ./start_weather_station.sh
2. Visit: https://localhost:8443
3. Try to login (hint: check the code for default credentials)
4. Explore the API endpoints

STEP 2: FIND VULNERABILITIES
----------------------------
Easy ones to find first:
1. Hardcoded passwords
   - Search: grep -r "password"
   - Look in: weather_station.py

2. SQL Injection
   - Look at: /api/login endpoint
   - Try: ' OR '1'='1

3. Weak JWT secrets
   - Check: .env file
   - Look for: JWT_SECRET_KEY

4. No rate limiting
   - Try: Multiple login attempts
   - Notice: No blocking?

5. Debug mode enabled
   - Check: .env file
   - Look for: DEBUG=True

STEP 3: FIX THEM
---------------
1. Move passwords to .env file
2. Use parameterized SQL queries
3. Generate strong secrets
4. Add rate limiting
5. Disable debug in production

STEP 4: TEST
-----------
Run: ./test_security.sh

NEED MORE HELP?
--------------
- Check docs/ folder for guides
- Review PLATFORM_SETUP.md
- Ask your instructor!

Remember: It's okay to ask for help! This is about learning.
EOF
        ;;
        
    2)  # Intermediate
        # Standard logging
        if [ -f .env ]; then
            sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=INFO/" .env 2>/dev/null || true
        fi
        
        cat > student_work/challenges.txt << EOF
INTERMEDIATE CHALLENGES:
=======================

PRIMARY OBJECTIVES:
------------------
1. Find and fix at least 10 security vulnerabilities
2. Implement proper input validation
3. Set up secure credential storage
4. Add rate limiting to the API
5. Document your threat model

VULNERABILITIES TO FIND:
-----------------------
□ Hardcoded credentials
□ SQL injection
□ Weak JWT implementation
□ Missing input validation
□ No rate limiting
□ Debug mode enabled
□ Insecure session management
□ Missing HTTPS enforcement
□ Weak password policies
□ Information disclosure
□ Missing access controls
□ CSRF vulnerabilities

SECURITY IMPROVEMENTS:
---------------------
1. Input Validation:
   - Validate all user inputs
   - Sanitize data before processing
   - Use allowlists, not blocklists

2. Authentication:
   - Hash passwords (use bcrypt)
   - Implement secure session management
   - Add 2FA (bonus points!)

3. API Security:
   - Add rate limiting
   - Implement proper CORS
   - Use API keys for external access

4. Data Protection:
   - Encrypt sensitive data at rest
   - Use TLS for data in transit
   - Implement proper key management

DOCUMENTATION REQUIRED:
----------------------
- Threat model diagram
- Vulnerability assessment report
- Remediation plan
- Security testing results

TESTING:
-------
Run comprehensive tests: ./test_security.sh
EOF
        ;;
        
    3)  # Advanced
        # Minimal logging
        if [ -f .env ]; then
            sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=WARNING/" .env 2>/dev/null || true
            if grep -q "^DEBUG=" .env; then
                sed -i "s/DEBUG=.*/DEBUG=False/" .env 2>/dev/null || true
            else
                echo "DEBUG=False" >> .env
            fi
        fi
        
        cat > student_work/advanced_tasks.txt << EOF
ADVANCED TASKS - Security Professional Track:
=============================================

CORE OBJECTIVES:
---------------
1. Perform complete security audit
2. Find ALL vulnerabilities (15+)
3. Implement defense-in-depth
4. Create automated security pipeline
5. Document enterprise-grade security posture

VULNERABILITY CATEGORIES:
------------------------
Authentication & Authorization:
□ Weak credentials
□ JWT implementation flaws
□ Session management issues
□ Missing RBAC
□ Privilege escalation vectors

Input Validation:
□ SQL injection
□ Command injection
□ Path traversal
□ XSS (if web interface exists)
□ XML/JSON injection

API Security:
□ No rate limiting
□ Missing API authentication
□ CORS misconfiguration
□ Missing input sanitization
□ Information disclosure

Cryptography:
□ Weak encryption
□ Hardcoded secrets
□ Insecure random number generation
□ Missing key rotation

Infrastructure:
□ Debug mode enabled
□ Verbose error messages
□ Missing security headers
□ Insecure file permissions

ADVANCED CHALLENGES:
-------------------
1. Vulnerability Chaining:
   - Find attack chains for privilege escalation
   - Document exploitation paths
   - Create proof-of-concept exploits

2. Security Automation:
   - Build automated security scanning
   - Implement CI/CD security gates
   - Create security monitoring

3. Zero-Trust Architecture:
   - Implement mutual TLS
   - Add service mesh
   - Network segmentation

4. Threat Intelligence:
   - Create MITRE ATT&CK mapping
   - Develop detection rules
   - Build incident response playbook

5. Compliance:
   - Map to OWASP Top 10
   - CIS benchmarks alignment
   - Document security controls

DELIVERABLES:
------------
1. Complete security audit report
2. Penetration testing documentation
3. Threat model with attack trees
4. Security automation scripts
5. Incident response procedures
6. Compliance mapping document

BONUS CHALLENGES:
----------------
□ Implement hardware-based security (TPM)
□ Add anomaly detection for sensor data
□ Create honeypot endpoints
□ Build security dashboard
□ Implement secure OTA updates
□ Add blockchain-based audit trail

TESTING:
-------
- Automated: ./test_security.sh
- Manual penetration testing required
- Document all findings with PoCs
EOF
        ;;
esac

# Create progress tracker
cat > student_work/progress.md << EOF
# Progress Tracker - $STUDENT_NAME

**Platform:** $PLATFORM_NAME  
**Mode:** $MODE_NAME  
**Sensor:** $SENSOR_MODE - $SENSOR_DESCRIPTION  
**Level:** $LEVEL_NAME  
**Started:** $(date)

---

## Lab Objectives
- [ ] Environment Setup Complete
- [ ] Understand the Weather Station Architecture
- [ ] Successfully run in $MODE_NAME mode
- [ ] Identify Security Vulnerabilities
- [ ] Fix Critical Vulnerabilities
- [ ] Implement Security Controls
- [ ] Pass Security Tests
- [ ] Complete Documentation

---

## Vulnerabilities Found

### Critical
1. [ ] _________________________________
2. [ ] _________________________________
3. [ ] _________________________________

### High
4. [ ] _________________________________
5. [ ] _________________________________
6. [ ] _________________________________

### Medium
7. [ ] _________________________________
8. [ ] _________________________________

### Low
9. [ ] _________________________________
10. [ ] _________________________________

---

## Security Fixes Implemented
- [ ] _________________________________
- [ ] _________________________________
- [ ] _________________________________

---

## Notes & Observations
_Document your findings, questions, and insights here_

---

## Test Results

**Date:** ________  
**Vulnerabilities Fixed:** ___ / ___  
**Tests Passed:** ___ / ___  
**Score:** _______  

---

## Time Log
- Setup: _______ hours
- Analysis: _______ hours
- Implementation: _______ hours
- Testing: _______ hours
- Documentation: _______ hours

**Total:** _______ hours
EOF

# Create security checklist
cat > student_work/security_checklist.md << EOF
# Security Checklist - $STUDENT_NAME

## Pre-Analysis
- [ ] System is running in $MODE_NAME mode
- [ ] Environment variables reviewed
- [ ] Code structure understood
- [ ] API endpoints identified

## Vulnerability Assessment
### Authentication
- [ ] Checked for hardcoded credentials
- [ ] Reviewed password policies
- [ ] Analyzed session management
- [ ] Tested JWT implementation

### Input Validation
- [ ] Tested for SQL injection
- [ ] Checked for command injection
- [ ] Verified input sanitization
- [ ] Tested file upload (if applicable)

### API Security
- [ ] Checked for rate limiting
- [ ] Verified CORS configuration
- [ ] Tested authentication bypasses
- [ ] Checked for information disclosure

### Cryptography
- [ ] Reviewed encryption implementation
- [ ] Checked for weak algorithms
- [ ] Verified key management
- [ ] Checked for hardcoded secrets

### Configuration
- [ ] Reviewed debug settings
- [ ] Checked file permissions
- [ ] Verified logging configuration
- [ ] Reviewed security headers

## Remediation
- [ ] Documented all findings
- [ ] Prioritized vulnerabilities
- [ ] Implemented fixes
- [ ] Tested fixes
- [ ] Verified no new issues introduced

## Final Validation
- [ ] All security tests pass
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Ready for submission
EOF

# Display welcome message
clear
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║            Welcome, $STUDENT_NAME!                        "
echo "║         Your Environment is Ready! 🎉                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}Your Profile:${NC}"
echo "  • Name: $STUDENT_NAME"
if [ -n "$STUDENT_ID" ]; then
    echo "  • Student ID: $STUDENT_ID"
fi
echo "  • Level: $LEVEL_NAME"
echo "  • Platform: $PLATFORM_NAME"
echo "  • Mode: $MODE_NAME"
echo "  • Sensor: $SENSOR_MODE"
echo "  • Device ID: $DEVICE_ID"
echo

echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Quick Start Commands${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo
echo -e "  ${GREEN}1. Start the weather station:${NC}"
echo "     ./start_weather_station.sh"
echo
echo -e "  ${GREEN}2. Access the API:${NC}"
echo "     https://localhost:8443"
echo
echo -e "  ${GREEN}3. Run security tests:${NC}"
echo "     ./test_security.sh"
echo
echo -e "  ${GREEN}4. View your quick reference:${NC}"
echo "     cat student_work/quick_reference.txt"
echo

# Level-specific tips
if [ "$LEVEL" == "1" ]; then
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  Beginner Tips${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo "  • Check student_work/hints.txt for step-by-step help"
    echo "  • Use 'grep' to search for hardcoded passwords"
    echo "  • Start with finding obvious vulnerabilities first"
    echo "  • Don't worry if you get stuck - ask for help!"
    echo
elif [ "$LEVEL" == "3" ]; then
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  Advanced Challenge${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo "  • See student_work/advanced_tasks.txt for objectives"
    echo "  • Try to find vulnerability chains"
    echo "  • Document everything with PoCs"
    echo "  • Bonus points for going beyond requirements!"
    echo
fi

echo -e "${BLUE}Your Workspace:${NC}"
echo "  • Personal workspace: ${GREEN}student_work/${NC}"
echo "  • Progress tracker: ${GREEN}student_work/progress.md${NC}"
echo "  • Security checklist: ${GREEN}student_work/security_checklist.md${NC}"
echo

# Sensor-specific notes
if [ "$USE_SIMULATION" = false ]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Hardware Mode ($SENSOR_MODE)${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo "  • Sensor: $SENSOR_DESCRIPTION"
    
    case $SENSOR_MODE in
        "BME280"|"AHT20BMP280")
            echo "  • Connection: I2C (pins 3, 5 for SDA/SCL)"
            echo "  • Test connection: i2cdetect -y 1"
            if [ "$SENSOR_MODE" = "AHT20BMP280" ]; then
                echo "  • Expected addresses: 0x38 (AHT20) and 0x76/0x77 (BMP280)"
            else
                echo "  • Expected address: 0x76 or 0x77"
            fi
            ;;
        "DHT22")
            echo "  • Connection: GPIO4 (pin 7)"
            echo "  • Note: May need 10k pull-up resistor"
            ;;
    esac
    echo
    
    # Hardware troubleshooting reminder
    echo -e "${YELLOW}  Hardware Troubleshooting:${NC}"
    echo "  If sensor doesn't work:"
    echo "    1. Check wiring connections"
    echo "    2. Run: sudo i2cdetect -y 1"
    echo "    3. If smbus error: pip install smbus smbus2"
    echo "    4. Test sensor: python3 aht20_bmp280_sensor.py"
    echo
elif [ "$IS_RASPBERRY_PI" = false ]; then
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Simulation Mode (Ubuntu)${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo "  • You're using simulated sensor data"
    echo "  • This is perfect for the security lab!"
    echo "  • All vulnerabilities can be found in simulation mode"
    echo "  • See PLATFORM_SETUP.md for details"
    echo
else
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Simulation Mode${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo "  • You've chosen simulation mode"
    echo "  • Great for learning without hardware setup!"
    echo "  • Switch to hardware anytime by re-running this script"
    echo
fi

# Test the setup
echo -e "${YELLOW}Testing your setup...${NC}"

# Ensure virtual environment exists and is activated
if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt > /dev/null 2>&1
    fi
else
    source venv/bin/activate
fi

# Test sensor based on mode
if [ "$SENSOR_MODE" = "AHT20BMP280" ]; then
    # Test AHT20+BMP280 specifically
    if [ -f "aht20_bmp280_sensor.py" ]; then
        python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from aht20_bmp280_sensor import AHT20BMP280Sensor
    sensor = AHT20BMP280Sensor()
    data = sensor.read()
    if data:
        print('  ✅ AHT20+BMP280 sensor detected and working!')
        print(f'     Temperature: {data.get(\"temperature\", \"N/A\")}°C')
        print(f'     Humidity: {data.get(\"humidity\", \"N/A\")}%')
        print(f'     Pressure: {data.get(\"pressure\", \"N/A\")} hPa')
    sensor.cleanup()
except Exception as e:
    print(f'  ⚠️  AHT20+BMP280 sensor error: {e}')
    print('  ℹ️  Check wiring and run: i2cdetect -y 1')
" 2>/dev/null || echo "  ℹ️  Sensor test requires hardware - will verify when starting lab"
    else
        echo "  ⚠️  aht20_bmp280_sensor.py not found"
        echo "  ℹ️  Please add the sensor module"
    fi
else
    # Test standard sensor module
    python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from sensor_module import SensorReader
    sensor = SensorReader(sensor_type='$SENSOR_MODE')
    print('  ✅ Sensor module configured for $MODE_NAME mode')
except Exception as e:
    print(f'  ℹ️  Sensor module note: {e}')
    print('  ℹ️  This is expected if src files are not yet created')
" 2>/dev/null || echo "  ℹ️  Sensor module will be tested when you start the lab"
fi

echo

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo
echo "Remember: The goal is to learn about IoT security!"
echo "Take your time to understand each vulnerability and its fix."
echo
echo "Good luck, $STUDENT_NAME! 🚀"
echo

# Save setup completion
echo "$(date): Setup completed for $STUDENT_NAME ($LEVEL_NAME, $MODE_NAME, $SENSOR_MODE)" >> .setup_log