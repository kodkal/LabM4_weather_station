# Setup Guide
## Detailed Installation and Configuration Instructions

---

## Quick Start (One Command)

```bash
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash
```

That's it! This command handles everything automatically.

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Automatic Installation](#2-automatic-installation)
3. [Manual Installation](#3-manual-installation)
4. [Configuration](#4-configuration)
5. [Running the Application](#5-running-the-application)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Prerequisites

### Hardware Requirements
- Raspberry Pi 4 (2GB+ RAM) or Pi 3B+
- 16GB+ MicroSD card
- Power supply (5V, 3A for Pi 4)
- Network connection (Ethernet or WiFi)

### Software Requirements
- Raspberry Pi OS Lite or Desktop (latest)
- Python 3.9 or higher
- Internet connection for package downloads

### Optional Hardware
- BME280 sensor (I2C)
- DHT22 sensor (GPIO)
- Breadboard and jumper wires

---

## 2. Automatic Installation

### Step 1: Connect to Your Pi
```bash
ssh pi@[YOUR_PI_IP]
# Default password: raspberry
```

### Step 2: Run Installation Script
```bash
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash
```

### Step 3: Personalize Setup
```bash
cd ~/LabM4_weather_station
./setup/student_onboard.sh
```

The automatic installation will:
- ✅ Update system packages
- ✅ Install Python and dependencies
- ✅ Clone the repository
- ✅ Set up virtual environment
- ✅ Configure hardware interfaces
- ✅ Generate SSL certificates
- ✅ Create necessary directories
- ✅ Set proper permissions

---

## 3. Manual Installation

### Step 1: Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install System Dependencies
```bash
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    i2c-tools \
    python3-smbus
```

### Step 3: Clone Repository
```bash
cd ~
git clone https://github.com/kodkal/LabM4_weather_station.git
cd LabM4_weather_station
```

### Step 4: Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Python Packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Enable Hardware Interfaces
```bash
# Enable I2C
sudo raspi-config nonint do_i2c 0

# Enable SPI (if needed)
sudo raspi-config nonint do_spi 0

# Add user to hardware groups
sudo usermod -a -G gpio,i2c,spi,dialout $USER
```

### Step 7: Create Directories
```bash
mkdir -p keys logs data data_backup
chmod 700 keys
chmod 755 logs data data_backup
```

### Step 8: Generate SSL Certificates
```bash
openssl req -x509 -newkey rsa:4096 \
    -keyout keys/private.key \
    -out keys/certificate.crt \
    -days 365 -nodes \
    -subj "/C=US/ST=Utah/L=Provo/O=UVU/CN=weather-station.local"

chmod 600 keys/private.key
chmod 644 keys/certificate.crt
```

### Step 9: Configure Environment
```bash
cp .env.example .env
nano .env  # Edit configuration
```

---

## 4. Configuration

### 4.1 Environment Variables (.env)

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit with your settings:
```ini
# Sensor Configuration
SENSOR_TYPE=AUTO           # AUTO, BME280, DHT22, or SIMULATED
SENSOR_SIMULATION=false     # Set true for simulation mode
SENSOR_PIN=4               # GPIO pin for DHT22

# Security
SECRET_KEY=[generate-secure-key]
JWT_SECRET=[generate-secure-key]

# Device
DEVICE_ID=weather-station-001
LOCATION=Your-Location

# API
API_PORT=8443
DEBUG=False
```

Generate secure keys:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4.2 Hardware Configuration

#### BME280 Wiring (I2C)
| BME280 Pin | Raspberry Pi Pin |
|------------|------------------|
| VCC | Pin 1 (3.3V) |
| GND | Pin 6 (Ground) |
| SCL | Pin 5 (GPIO3) |
| SDA | Pin 3 (GPIO2) |

#### DHT22 Wiring
| DHT22 Pin | Raspberry Pi Pin |
|-----------|------------------|
| VCC | Pin 2 (5V) |
| Data | Pin 7 (GPIO4) |
| GND | Pin 6 (Ground) |

### 4.3 Firewall Configuration
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8443/tcp comment 'Weather Station API'
sudo ufw enable
```

---

## 5. Running the Application

### 5.1 Quick Start
```bash
cd ~/LabM4_weather_station
./start_weather_station.sh
```

### 5.2 Manual Start
```bash
cd ~/LabM4_weather_station
source venv/bin/activate
python src/weather_station.py
```

### 5.3 Run in Background
```bash
nohup python src/weather_station.py > weather.log 2>&1 &
```

### 5.4 Run as Service
Create systemd service:
```bash
sudo nano /etc/systemd/system/weather-station.service
```

Add content:
```ini
[Unit]
Description=Weather Station IoT Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/LabM4_weather_station
Environment="PATH=/home/pi/LabM4_weather_station/venv/bin"
ExecStart=/home/pi/LabM4_weather_station/venv/bin/python /home/pi/LabM4_weather_station/src/weather_station.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-station
sudo systemctl start weather-station
sudo systemctl status weather-station
```

### 5.5 Accessing the API
```bash
# Local access
curl https://localhost:8443/api/status

# Remote access
curl https://[PI_IP]:8443/api/status
```

---

## 6. Troubleshooting

### 6.1 Common Issues and Solutions

#### Installation Fails
```bash
# Check internet connection
ping -c 3 github.com

# Check Python version
python3 --version  # Should be 3.9+

# Try manual installation
git clone https://github.com/kodkal/LabM4_weather_station.git
```

#### Module Not Found Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install --upgrade -r requirements.txt
```

#### Sensor Not Detected
```bash
# Check I2C is enabled
sudo i2cdetect -y 1

# Should show address 76 or 77 for BME280
# Check wiring connections
# Try simulation mode
export SENSOR_SIMULATION=true
```

#### Permission Denied
```bash
# Add user to groups
sudo usermod -a -G gpio,i2c,spi $USER

# Logout and login again
# Or use newgrp
newgrp gpio
```

#### SSL Certificate Issues
```bash
# Regenerate certificates
cd ~/LabM4_weather_station
openssl req -x509 -newkey rsa:4096 \
    -keyout keys/private.key \
    -out keys/certificate.crt \
    -days 365 -nodes

chmod 600 keys/private.key
```

### 6.2 Checking Logs
```bash
# Application logs
tail -f logs/weather_station.log

# System logs
sudo journalctl -u weather-station -f

# Python errors
python src/weather_station.py 2>&1 | tee debug.log
```

### 6.3 Testing Components

#### Test Sensor Module
```bash
python -c "
from src.sensor_module import SensorReader
sensor = SensorReader('SIMULATED')
print(sensor.read_sensor())
"
```

#### Test Security Module
```bash
python -c "
from src.security.auth import JWTManager
jwt = JWTManager()
token = jwt.generate_token({'user': 'test'})
print('Token generated successfully')
"
```

#### Test API
```bash
# Start application in one terminal
python src/weather_station.py

# Test in another terminal
curl -X POST http://localhost:8080/api/login \
    -H "Content-Type: application/json" \
    -d '{"username": "test", "password": "test"}'
```

### 6.4 Reset and Start Over

#### Soft Reset (keep installation)
```bash
cd ~/LabM4_weather_station/setup
./reset_lab.sh soft
```

#### Hard Reset (complete removal)
```bash
cd ~/LabM4_weather_station/setup
./reset_lab.sh hard

# Then reinstall
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash
```

---

## 7. Verification

### 7.1 Verify Installation
```bash
cd ~/LabM4_weather_station

# Check Python packages
pip list | grep -E "flask|jwt|cryptography"

# Check directories
ls -la keys/ logs/ data/

# Test simulation
export SENSOR_SIMULATION=true
python -c "from src.sensor_module import SensorReader; print('✓ Installation OK')"
```

### 7.2 Security Verification
```bash
# Run security tests
python tests/test_security.py

# Check for hardcoded secrets
grep -r "password\|secret\|api_key" src/ --include="*.py"
```

---

## 8. Next Steps

1. **Run the application**: `./start_weather_station.sh`
2. **Test security**: `./test_security.sh`
3. **Read documentation**: Check `docs/` folder
4. **Start fixing vulnerabilities**: Follow STUDENT_GUIDE.md

---

## 9. Support

- **Documentation**: `/docs` folder
- **Quick Reference**: `cat student_work/quick_reference.txt`
- **GitHub Issues**: https://github.com/kodkal/LabM4_weather_station/issues
- **Instructor Help**: [Contact information]

---

*Setup Guide v1.0 | Weather Station IoT Security Lab*