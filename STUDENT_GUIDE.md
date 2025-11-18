# Student Guide: Secure Weather Station Project
## Module 4 - IoT Security Course | UVU

---

## Welcome to IoT Security!

This project will teach you how to build a secure IoT weather station from the ground up. You'll implement real security controls used in professional IoT deployments while learning practical skills that are directly applicable to industry.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Hardware Setup](#hardware-setup)
4. [Software Installation](#software-installation)
5. [Project Milestones](#project-milestones)
6. [Security Implementation Guide](#security-implementation-guide)
7. [Testing Your Implementation](#testing-your-implementation)
8. [Troubleshooting](#troubleshooting)
9. [Project Submission](#project-submission)
10. [Learning Resources](#learning-resources)

---

## Project Overview

### What You'll Build
You'll create a secure weather monitoring station that:
- Reads temperature, humidity, and pressure data from sensors
- Implements secure boot verification
- Encrypts all data transmissions using TLS/SSL
- Uses JWT tokens for API authentication
- Validates all inputs to prevent injection attacks
- Stores credentials securely with encryption

### Learning Objectives
By completing this project, you will:
- ✅ Understand IoT security fundamentals
- ✅ Implement encryption and secure communications
- ✅ Build secure authentication systems
- ✅ Prevent common security vulnerabilities
- ✅ Create professional security documentation

### Time Commitment
- **Total Duration**: 4 weeks
- **Expected Weekly Time**: 8-10 hours
  - Class/Lab: 3 hours
  - Implementation: 3-4 hours
  - Documentation: 1-2 hours
  - Testing: 1 hour

---

## Getting Started

### Prerequisites Checklist
Before starting, ensure you have:
- [ ] Basic Python programming knowledge
- [ ] Familiarity with Linux command line
- [ ] GitHub account for code submission
- [ ] Access to required hardware (see list below)
- [ ] Computer with SSH client

### Required Hardware
```
Essential Components:
□ Raspberry Pi 4 (2GB+ RAM) or Pi 3B+        ($35-55)
□ MicroSD Card (16GB+, Class 10)             ($8-15)
□ Power Supply (5V, 3A for Pi 4)             ($10-15)
□ BME280 or DHT22 sensor                     ($10-20)
□ Breadboard                                  ($5-10)
□ Jumper wires (male-to-female)              ($5-10)
                                Total: ~$75-125

Optional but Helpful:
□ Raspberry Pi case                          ($10)
□ Heat sinks                                 ($5)
□ HDMI cable (for initial setup)             ($10)
□ USB keyboard (for initial setup)           ($15)
```

### Software Requirements
- Raspberry Pi OS Lite (latest version)
- Python 3.9 or higher
- Git
- Code editor (VS Code recommended)

---

## Hardware Setup

### Step 1: Prepare the Raspberry Pi

#### 1.1 Flash the Operating System
```bash
# Download Raspberry Pi Imager from:
https://www.raspberrypi.org/software/

# Flash Raspberry Pi OS Lite to your SD card
# Enable SSH in advanced options
# Configure WiFi if not using Ethernet
```

#### 1.2 Initial Boot Configuration
```bash
# Connect via SSH (default password: raspberry)
ssh pi@raspberrypi.local

# IMMEDIATELY change the default password
passwd

# Update the system
sudo apt update && sudo apt upgrade -y

# Configure timezone
sudo timedatectl set-timezone America/Denver

# Enable required interfaces
sudo raspi-config
# Enable: I2C, SPI (if needed)
```

### Step 2: Connect the Sensor

#### Option A: BME280 Sensor (I2C)
```
BME280 Pin  →  Raspberry Pi Pin
VIN/VCC     →  Pin 1 (3.3V)
GND         →  Pin 6 (Ground)
SCL         →  Pin 5 (GPIO3/SCL)
SDA         →  Pin 3 (GPIO2/SDA)
```

#### Option B: DHT22 Sensor
```
DHT22 Pin   →  Raspberry Pi Pin
VCC         →  Pin 2 (5V)
Data        →  Pin 7 (GPIO4)
GND         →  Pin 6 (Ground)

Note: Add a 10kΩ pull-up resistor between VCC and Data
```

#### Verify Sensor Connection
```bash
# For BME280 (I2C)
sudo i2cdetect -y 1
# Should show address 76 or 77

# For DHT22
# Test will be done via Python code
```

---

## Software Installation

### Step 1: Clone the Project Repository
```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/[instructor-repo]/secure-weather-station.git
cd secure-weather-station

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
# Install system packages
sudo apt install -y python3-pip python3-dev git
sudo apt install -y libssl-dev libffi-dev
sudo apt install -y i2c-tools python3-smbus

# Install Python packages
pip install -r requirements.txt
```

### Step 3: Initial Configuration
```bash
# Create necessary directories
mkdir -p keys logs data data_backup

# Set proper permissions
chmod 700 keys
chmod 755 logs data

# Copy configuration template
cp config/settings.example.py config/settings.py

# Edit configuration with your settings
nano config/settings.py
```

---

## Project Milestones

### Week 1: Secure Foundation ✓
**Goal**: Set up secure Raspberry Pi and implement boot security

**Tasks**:
1. **Secure the Raspberry Pi**
   ```bash
   # Disable unnecessary services
   sudo systemctl disable bluetooth
   sudo systemctl disable avahi-daemon
   
   # Configure firewall
   sudo apt install ufw
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow ssh
   sudo ufw allow 8443/tcp  # For HTTPS API
   sudo ufw enable
   ```

2. **Implement Secure Boot Verification**
   ```python
   # In weather_station.py
   def verify_secure_boot(self):
       # Your implementation here
       # Check file integrity
       # Verify configurations
       # Log security events
   ```

3. **Create Security Baseline**
   - Document initial configuration
   - Create file integrity checksums
   - Set up logging

**Deliverables**:
- [ ] Hardened Pi configuration
- [ ] Working secure boot verification
- [ ] Security baseline document

### Week 2: Encryption & Communication ✓
**Goal**: Implement encrypted data transmission

**Tasks**:
1. **Generate SSL Certificates**
   ```bash
   # Create certificate authority
   ./setup/generate_certs.sh
   
   # Or generate self-signed certificate
   openssl req -x509 -newkey rsa:4096 -keyout keys/private.key \
     -out keys/certificate.crt -days 365 -nodes
   ```

2. **Implement Data Encryption**
   ```python
   # Multiple encryption methods
   - Fernet (symmetric)
   - AES-256-GCM
   - RSA (asymmetric)
   ```

3. **Test Secure Transmission**
   - Verify with Wireshark
   - Check certificate validation
   - Measure encryption overhead

**Deliverables**:
- [ ] Working encryption module
- [ ] Valid SSL certificates
- [ ] Encrypted data transmission proof

### Week 3: Authentication & API ✓
**Goal**: Build secure API with authentication

**Tasks**:
1. **Implement JWT Authentication**
   ```python
   # Generate tokens
   token = jwt_manager.generate_token(payload)
   
   # Verify tokens
   is_valid, data = jwt_manager.verify_token(token)
   ```

2. **Create RESTful API**
   ```python
   # API Endpoints
   GET  /api/status       - System status
   GET  /api/data         - Sensor data
   POST /api/auth/login   - Authenticate
   POST /api/auth/refresh - Refresh token
   ```

3. **Add Rate Limiting**
   - Prevent brute force attacks
   - Implement per-IP limits
   - Add exponential backoff

**Deliverables**:
- [ ] Working API with authentication
- [ ] JWT implementation
- [ ] Rate limiting active

### Week 4: Validation & Storage ✓
**Goal**: Implement input validation and secure storage

**Tasks**:
1. **Input Validation**
   ```python
   # Validate all inputs
   validator = InputValidator(strict_mode=True)
   is_valid, error = validator.validate(
       user_input, 
       DataType.STRING
   )
   ```

2. **Secure Credential Storage**
   ```python
   # Store credentials securely
   credential_store.store_credential(
       name="api_key",
       value=secret_value,
       expires_in=timedelta(days=30)
   )
   ```

3. **Complete Security Testing**
   - Test injection prevention
   - Verify credential encryption
   - Audit access logs

**Deliverables**:
- [ ] Input validation working
- [ ] Secure credential storage
- [ ] Security test results

---

## Security Implementation Guide

### 1. Secure Boot Implementation
```python
# Example: Boot Integrity Check
import hashlib
import os

def calculate_boot_hash():
    """Calculate hash of critical boot files"""
    hasher = hashlib.sha256()
    critical_files = [
        '/boot/config.txt',
        '/boot/cmdline.txt',
        sys.executable
    ]
    
    for filepath in critical_files:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                hasher.update(f.read())
    
    return hasher.hexdigest()

# Store hash on first boot, verify on subsequent boots
```

### 2. Encryption Best Practices
```python
# Never hardcode keys!
# BAD:
SECRET_KEY = "my-secret-key-123"

# GOOD:
import os
from cryptography.fernet import Fernet

def load_or_create_key():
    key_file = 'keys/encryption.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        os.chmod(key_file, 0o600)  # Restrict access
        return key
```

### 3. JWT Authentication Pattern
```python
# Secure token generation
def generate_secure_token(user_data):
    payload = {
        'user_id': user_data['id'],
        'device_id': user_data['device_id'],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24),
        'jti': secrets.token_urlsafe(16)  # Unique ID
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

### 4. Input Validation Examples
```python
# Prevent SQL Injection
def validate_sensor_id(sensor_id):
    # Whitelist approach
    if not re.match(r'^[a-zA-Z0-9-]{8,36}$', sensor_id):
        raise ValidationError("Invalid sensor ID format")
    return sensor_id

# Prevent Command Injection
def sanitize_filename(filename):
    # Remove dangerous characters
    safe_chars = re.compile(r'[^a-zA-Z0-9._-]')
    return safe_chars.sub('', filename)
```

---

## Testing Your Implementation

### Security Testing Checklist

#### 1. Boot Security Tests
```bash
# Test 1: Modify a boot file
sudo echo "test" >> /boot/config.txt
# Your system should detect this change

# Test 2: Check logging
grep "boot_verification" logs/weather_station.log
```

#### 2. Encryption Tests
```bash
# Test with Wireshark
sudo tcpdump -i any -w capture.pcap port 8443

# Verify no plaintext data is visible
wireshark capture.pcap
```

#### 3. Authentication Tests
```python
# Test invalid token
curl -X GET https://localhost:8443/api/data \
  -H "Authorization: Bearer invalid_token"
# Should return 401 Unauthorized

# Test expired token
# Generate token with 1-second expiry, wait, then use
```

#### 4. Injection Tests
```python
# Test SQL injection attempts
test_inputs = [
    "'; DROP TABLE sensors; --",
    "1 OR 1=1",
    "../../../etc/passwd",
    "<script>alert('XSS')</script>"
]

for malicious_input in test_inputs:
    # All should be rejected by validation
```

### Performance Testing
```python
# Measure encryption overhead
import time

def test_encryption_performance():
    data = {"temperature": 22.5, "humidity": 60}
    
    # Test 1000 encryptions
    start = time.time()
    for _ in range(1000):
        encrypted = secure_transmission.encrypt_data(data)
    
    elapsed = time.time() - start
    print(f"1000 encryptions: {elapsed:.2f} seconds")
    print(f"Average: {elapsed/1000*1000:.2f} ms per encryption")
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Permission denied" errors
```bash
# Solution: Add user to required groups
sudo usermod -a -G gpio,i2c,spi,dialout $USER
# Logout and login again
```

#### Issue: Sensor not detected
```bash
# For I2C sensors:
# 1. Check wiring (use multimeter)
# 2. Verify I2C is enabled
sudo raspi-config  # Interface Options > I2C

# 3. Scan I2C bus
sudo i2cdetect -y 1

# 4. Check pull-up resistors (required for I2C)
```

#### Issue: "Module not found" errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install --upgrade -r requirements.txt
```

#### Issue: SSL certificate errors
```python
# For development/testing only:
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# For production: Generate proper certificates
```

#### Issue: JWT token always invalid
```python
# Check:
1. System time is correct (JWT uses timestamps)
   date
   sudo ntpdate -s time.nist.gov

2. Secret key matches between generation and validation

3. Algorithm matches (HS256 vs RS256)
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
logger.debug(f"Token payload: {payload}")
logger.debug(f"Validation result: {is_valid}")
```

---

## Project Submission

### Required Deliverables

#### 1. Code Repository
Your GitHub repository should include:
```
secure-weather-station/
├── src/                    # All source code
│   ├── weather_station.py  # Main application
│   ├── sensor_module.py    # Sensor interface
│   ├── security/           # Security modules
│   └── api/               # API implementation
├── tests/                 # Test files
├── docs/                  # Documentation
│   ├── SECURITY_DESIGN.md # Your security design
│   ├── THREAT_MODEL.md    # Your threat model
│   └── API_DOCS.md       # API documentation
├── logs/                  # Log samples
├── requirements.txt       # Dependencies
└── README.md             # Project overview
```

#### 2. Security Design Document
Must include:
- System architecture diagram
- Security controls implemented
- Data flow diagrams
- Encryption methods used
- Authentication flow
- Key management strategy

#### 3. Threat Model
Must address:
- Asset identification
- Threat actors
- Attack vectors
- Vulnerabilities
- Mitigation strategies
- Risk assessment

#### 4. Demo Video (5-10 minutes)
Show:
- System running
- Sensor data collection
- Encrypted transmission
- Authentication working
- Input validation
- Failed attack attempts

### Submission Checklist
Before submitting, ensure:
- [ ] All code is commented and documented
- [ ] README includes setup instructions
- [ ] Security features are working
- [ ] Tests pass successfully
- [ ] Documentation is complete
- [ ] No hardcoded secrets in code
- [ ] Repository is public (or instructor has access)

### Grading Criteria
- **Implementation (40%)**: Working features
- **Security (30%)**: Proper security controls
- **Documentation (20%)**: Clear, complete docs
- **Testing (10%)**: Evidence of security testing

---

## Learning Resources

### Essential Reading
1. **OWASP IoT Top 10**
   - [Link](https://owasp.org/www-project-internet-of-things/)
   - Focus on: Weak passwords, insecure network services, lack of encryption

2. **JWT Best Practices**
   - [JWT.io](https://jwt.io/introduction)
   - Understand: Structure, signing, validation

3. **Raspberry Pi Security**
   - [Official Guide](https://www.raspberrypi.org/documentation/configuration/security.md)
   - Focus on: SSH hardening, firewall, updates

### Video Tutorials
- [Raspberry Pi Security Hardening](https://www.youtube.com/watch?v=ukHcTCdOKrc)
- [JWT Authentication Explained](https://www.youtube.com/watch?v=soGRyl9ztjI)
- [IoT Security Best Practices](https://www.youtube.com/watch?v=_dSa1K9JGhc)

### Practice Resources
1. **PentesterLab**: IoT challenges
2. **HackTheBox**: IoT rooms
3. **TryHackMe**: IoT security path

### Documentation References
- [Python Cryptography Library](https://cryptography.io/en/latest/)
- [Flask Security Guide](https://flask.palletsprojects.com/en/2.0.x/security/)
- [Linux Security Modules](https://www.kernel.org/doc/html/latest/admin-guide/LSM/index.html)

---

## Tips for Success

### Time Management
- **Week 1-2**: Focus on getting basic functionality working
- **Week 3**: Add security features
- **Week 4**: Testing, documentation, and polish

### Best Practices
1. **Commit Often**: Use Git to track your progress
2. **Test Early**: Don't wait until the end to test
3. **Ask Questions**: Use office hours and forums
4. **Document as You Go**: Don't leave it until the end
5. **Security First**: Think about security in every component

### Common Mistakes to Avoid
- ❌ Hardcoding credentials
- ❌ Ignoring error handling
- ❌ Not testing edge cases
- ❌ Weak input validation
- ❌ Missing documentation

### Getting Help
- **Office Hours**: [Schedule]
- **Class Forum**: [Link]
- **Email**: [Instructor email]
- **Slack/Discord**: [Channel]

---

## Final Thoughts

This project simulates real-world IoT security challenges. The skills you learn here are directly applicable to:
- IoT product development
- Security engineering
- Penetration testing
- Security auditing
- Compliance implementation

Take your time to understand each security concept. It's better to implement fewer features correctly than to rush through everything.

Good luck with your secure weather station!

---

**Remember**: Security is not a feature, it's a mindset. Think like an attacker to build better defenses.

---

*Version 1.0 | Last Updated: November 2024*