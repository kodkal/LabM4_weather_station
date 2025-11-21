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

# Get student information
echo -e "${YELLOW}Welcome to the Weather Station Security Lab!${NC}"
echo
echo "Let's personalize your setup..."
echo

# Get student name
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

# Choose mode
echo
echo "How do you want to run the lab?"
echo "  1) Simulation Mode (no hardware needed)"
echo "  2) Hardware Mode (I have sensors connected)"
echo "  3) Auto-detect"
read -p "Enter choice [1-3]: " MODE

case $MODE in
    1) 
        SENSOR_MODE="SIMULATED"
        MODE_NAME="Simulation"
        ;;
    2) 
        SENSOR_MODE="BME280"
        MODE_NAME="Hardware"
        ;;
    *) 
        SENSOR_MODE="AUTO"
        MODE_NAME="Auto-detect"
        ;;
esac

# Create student profile
echo
echo -e "${BLUE}Creating your profile...${NC}"

cd "$PROJECT_DIR"

# Create student profile file
cat > .student_profile << EOF
# Student Profile - Weather Station Lab
STUDENT_NAME="$STUDENT_NAME"
STUDENT_ID="$STUDENT_ID"
LEVEL="$LEVEL_NAME"
MODE="$MODE_NAME"
START_DATE="$(date)"
SENSOR_TYPE="$SENSOR_MODE"
EOF

# Update .env with student settings
if [ -f .env ]; then
    # Update sensor type
    sed -i "s/SENSOR_TYPE=.*/SENSOR_TYPE=$SENSOR_MODE/" .env
    
    # Set simulation flag if needed
    if [ "$SENSOR_MODE" == "SIMULATED" ]; then
        sed -i "s/SENSOR_SIMULATION=.*/SENSOR_SIMULATION=true/" .env
    fi
    
    # Set device ID with student identifier
    DEVICE_ID="weather-$(echo $STUDENT_NAME | tr ' ' '-' | tr '[:upper:]' '[:lower:]')-$(date +%s | tail -c 5)"
    sed -i "s/DEVICE_ID=.*/DEVICE_ID=$DEVICE_ID/" .env
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

Student: $STUDENT_NAME
Level: $LEVEL_NAME
Mode: $MODE_NAME
Started: $(date)
EOF

# Generate quick reference card
cat > student_work/quick_reference.txt << EOF
========================================
 QUICK REFERENCE - $STUDENT_NAME
========================================

YOUR SETTINGS:
- Mode: $MODE_NAME
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

Activate Python Environment:
  source venv/bin/activate

View Your Profile:
  cat .student_profile

IMPORTANT FILES:
---------------
Main Code: src/weather_station.py
Your Work: student_work/
Config: .env
Logs: logs/weather_station.log

HELP:
----
Student Guide: docs/STUDENT_GUIDE.md
Simulation Guide: docs/SIMULATION_GUIDE.md

========================================
EOF

# Set up level-appropriate configurations
echo -e "${BLUE}Configuring for $LEVEL_NAME level...${NC}"

case $LEVEL in
    1)  # Beginner
        # Enable more logging
        sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=DEBUG/" .env 2>/dev/null || true
        sed -i "s/DEBUG=.*/DEBUG=True/" .env 2>/dev/null || true
        
        # Create beginner hints file
        cat > student_work/hints.txt << EOF
BEGINNER HINTS:
--------------
1. Start with the simulation mode to understand the system
2. Look for hardcoded passwords first (grep for "password")
3. Check the /api/login endpoint for SQL injection
4. Review the JWT token implementation
5. Use the test_security.py script to check your progress

Run security tests: python tests/test_security.py
EOF
        ;;
        
    2)  # Intermediate
        # Standard logging
        sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=INFO/" .env 2>/dev/null || true
        
        cat > student_work/challenges.txt << EOF
INTERMEDIATE CHALLENGES:
-----------------------
1. Find and fix at least 10 security vulnerabilities
2. Implement proper input validation
3. Set up secure credential storage
4. Add rate limiting to the API
5. Document your threat model
EOF
        ;;
        
    3)  # Advanced
        # Minimal logging
        sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=WARNING/" .env 2>/dev/null || true
        sed -i "s/DEBUG=.*/DEBUG=False/" .env 2>/dev/null || true
        
        cat > student_work/advanced_tasks.txt << EOF
ADVANCED TASKS:
--------------
1. Find ALL security vulnerabilities
2. Implement a complete security audit
3. Add penetration testing
4. Create automated security scanning
5. Build a secure CI/CD pipeline
6. Implement zero-trust architecture

BONUS: Try to chain vulnerabilities for privilege escalation!
EOF
        ;;
esac

# Create progress tracker
cat > student_work/progress.md << EOF
# Progress Tracker - $STUDENT_NAME

## Lab Objectives
- [ ] Environment Setup Complete
- [ ] Understand the Weather Station Architecture
- [ ] Run in Simulation Mode
- [ ] Identify Security Vulnerabilities
- [ ] Fix Critical Vulnerabilities
- [ ] Implement Security Controls
- [ ] Pass Security Tests
- [ ] Complete Documentation

## Vulnerabilities Found
1. [ ] _________________________________
2. [ ] _________________________________
3. [ ] _________________________________
4. [ ] _________________________________
5. [ ] _________________________________

## Notes
_Your notes here_

## Test Results
Date: ________
Score: _______
Grade: _______
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
echo "  • Level: $LEVEL_NAME"
echo "  • Mode: $MODE_NAME"
echo "  • Device ID: $DEVICE_ID"
echo

echo -e "${YELLOW}Quick Start:${NC}"
echo "  1. Start the weather station:"
echo "     ${GREEN}./start_weather_station.sh${NC}"
echo
echo "  2. In another terminal, test security:"
echo "     ${GREEN}./test_security.sh${NC}"
echo
echo "  3. View your quick reference:"
echo "     ${GREEN}cat student_work/quick_reference.txt${NC}"
echo

if [ "$LEVEL" == "1" ]; then
    echo -e "${MAGENTA}Beginner Tips:${NC}"
    echo "  • Start with simulation mode - it's easier!"
    echo "  • Check student_work/hints.txt for help"
    echo "  • Use grep to search for passwords"
    echo
fi

echo -e "${BLUE}Your workspace is in:${NC} student_work/"
echo -e "${BLUE}Track your progress in:${NC} student_work/progress.md"
echo

# Test the setup
echo -e "${YELLOW}Testing your setup...${NC}"
# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from sensor_module import SensorReader
    sensor = SensorReader(sensor_type='$SENSOR_MODE')
    print('✅ Sensor module OK')
except Exception as e:
    print(f'⚠️  Sensor test failed: {e}')
    print('   This is OK if you are using simulation mode!')
" || true

echo
echo -e "${GREEN}Setup complete! Good luck with the lab!${NC}"
echo
echo "Remember: The goal is to learn about IoT security, not just to get it working!"
echo "Take your time to understand each vulnerability and its fix."
echo

# Save setup completion
echo "$(date): Setup completed for $STUDENT_NAME" >> .setup_log