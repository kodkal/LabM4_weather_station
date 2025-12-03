# Student Guide: Secure Weather Station Project
## Module 4 - IoT Security Course | UVU

---

## 📋 Lab Requirements

### What You'll Receive
- ✅ **Raspberry Pi 4** (Pre-configured with Raspberry Pi OS)
- ✅ **Network Access** (Ethernet or WiFi credentials)
- ✅ **Power Supply** for Raspberry Pi
- ✅ **Lab Time**: 4 weeks to complete

### What You'll Submit
- 📸 **Screenshots** at each major step (detailed below)
- 📄 **Security Report** documenting vulnerabilities found and fixed
- 💾 **Your Code** with security improvements
- ✅ **Test Results** showing passing security tests

---

## 🚀 PART 1: Initial Setup (30 minutes)

### Step 1.1: Connect to Your Raspberry Pi

**Take Screenshot #1: SSH Connection**

1. Open Terminal (Mac/Linux) or PowerShell (Windows)
2. Connect via SSH:
```bash
ssh pi@[YOUR_PI_IP_ADDRESS]
# Example: ssh pi@192.168.1.100
```
3. Enter password when prompted (default: `raspberry`)
4. **📸 Screenshot: Show successful SSH connection with pi@raspberry prompt**

### Step 1.2: Run One-Line Installation

**Take Screenshot #2: Installation Start**

5. Copy and paste this EXACT command:
```bash
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash
```
6. **📸 Screenshot: Show the installation banner starting**
7. Wait for installation (5-10 minutes)
8. **📸 Screenshot #3: Show "Installation Complete! 🎉" message**

### Step 1.3: Student Onboarding (REQUIRED)

**Take Screenshot #4: Onboarding Process**

9. Run the onboarding script:
```bash
cd ~/LabM4_weather_station
./setu./setup/student_onboard.sh
```

10. Answer the prompts:
    - **Your Name**: Enter your full name
    - **Student ID**: Enter your UVU student ID
    - **Experience Level**: Choose 1 (Beginner), 2 (Intermediate), or 3 (Advanced)
    - **Mode**: Choose 1 (Simulation Mode) - no hardware needed!

11. **📸 Screenshot #5: Show your personalized welcome message with your name**

### Step 1.4: Verify Installation

**Take Screenshot #6: Installation Verification**

12. Check your profile:
```bash
cat .student_profile
```
13. **📸 Screenshot: Show your student profile contents**

14. View your quick reference:
```bash
cat student_work/quick_reference.txt
```
15. **📸 Screenshot #7: Show your personalized quick reference**

---

## 🔬 PART 2: Exploring the System (45 minutes)

### Step 2.1: Start the Weather Station

**Take Screenshot #8: Weather Station Running**

16. Start the application:
```bash
./start_weather_station.sh
```
17. **📸 Screenshot: Show "Weather Station initialized" message**
18. Press `Ctrl+C` to stop

### Step 2.2: Test Simulation Mode

**Take Screenshot #9: Simulation Test**

19. Run simulation test:
```bash
./test_simulation.sh
```
20. **📸 Screenshot: Show "TEST SUITE COMPLETE" with all tests**

### Step 2.3: Initial Security Test

**Take Screenshot #10: Baseline Security Score**

21. Run security test:
```bash
./test_security.sh
```
22. **📸 Screenshot: Show your initial security score (likely failing)**
23. **IMPORTANT**: Save this score - you'll compare it later!

---

## 🔍 PART 3: Finding Vulnerabilities (2 hours)

### Step 3.1: Switch to Vulnerable Version

**Take Screenshot #11: Vulnerable Version**

24. Activate vulnerable version:
```bash
cd ~/LabM4_weather_station
python scripts/manage_vulnerabilities.py switch vulnerable
```
25. **📸 Screenshot: Show "Switched to VULNERABLE version" message**

### Step 3.2: Search for Hardcoded Credentials

**Take Screenshot #12: Finding Secrets**

26. Search for passwords:
```bash
grep -r "password" --include="*.py" | head -10
```
27. **📸 Screenshot: Show grep results with hardcoded passwords**

28. Search for API keys:
```bash
grep -r "api_key\|secret" --include="*.py" | head -10
```
29. **📸 Screenshot #13: Show grep results with API keys/secrets**

### Step 3.3: Test for SQL Injection

**Take Screenshot #14: SQL Injection Test**

30. Start the weather station:
```bash
# In Terminal 1
./start_weather_station.sh
```

31. In a new terminal (Terminal 2), test SQL injection:
```bash
# In Terminal 2 (open new SSH session)
cd ~/LabM4_weather_station
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin'\'' OR '\''1'\''='\''1", "password": "test"}'
```
32. **📸 Screenshot: Show the curl command and response**

### Step 3.4: Document Vulnerabilities

**Take Screenshot #15: Progress Tracking**

33. Update your progress file:
```bash
nano student_work/progress.md
```
34. Add at least 5 vulnerabilities you found:
```markdown
## Vulnerabilities Found
1. ✓ Hardcoded password in weather_station.py line XX
2. ✓ SQL injection in login endpoint
3. ✓ API key exposed in source code
4. ✓ No input validation
5. ✓ Debug mode enabled in production
```
35. **📸 Screenshot: Show your progress.md with vulnerabilities listed**

---

## 🔧 PART 4: Fixing Vulnerabilities (2 hours)

### Step 4.1: Fix Hardcoded Credentials

**Take Screenshot #16: Environment Variables**

36. Edit the main file:
```bash
nano weather_station.py
```

37. Find and replace hardcoded values:
```python
# BEFORE (BAD):
API_KEY = "super_secret_api_key_12345"

# AFTER (GOOD):
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ.get('API_KEY')
```
38. **📸 Screenshot: Show your code fix for hardcoded credentials**

### Step 4.2: Fix SQL Injection

**Take Screenshot #17: SQL Fix**

39. Find the vulnerable SQL code:
```bash
grep -n "SELECT \* FROM users" weather_station.py
```

40. Fix it with parameterized queries:
```python
# BEFORE (VULNERABLE):
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

# AFTER (SECURE):
query = "SELECT * FROM users WHERE username=? AND password=?"
cursor.execute(query, (username, password))
```
41. **📸 Screenshot: Show your SQL injection fix**

### Step 4.3: Add Input Validation

**Take Screenshot #18: Input Validation**

42. Add validation function:
```python
def validate_input(user_input):
    # Check for dangerous characters
    if any(char in user_input for char in ['<', '>', ';', '--', 'script']):
        return False
    # Check length
    if len(user_input) > 255:
        return False
    return True
```
43. **📸 Screenshot: Show your input validation code**

---

## ✅ PART 5: Testing Your Fixes (1 hour)

### Step 5.1: Run Security Tests Again

**Take Screenshot #19: Improved Score**

44. Test your fixes:
```bash
cd ~/LabM4_weather_station
./test_security.sh
```
45. **📸 Screenshot: Show your improved security score**

### Step 5.2: Verify Specific Fixes

**Take Screenshot #20: SQL Injection Prevention**

46. Test SQL injection is fixed:
```bash
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin'\'' OR '\''1'\''='\''1", "password": "test"}'
```
47. **📸 Screenshot: Show that SQL injection now fails (401 error)**

### Step 5.3: Final Security Score

**Take Screenshot #21: Final Score**

48. Run final security test:
```bash
./test_security.sh | tee final_results.txt
```
49. **📸 Screenshot: Show your final security score with grade**

---

## 📊 PART 6: Documentation (1 hour)

### Step 6.1: Create Security Report

**Take Screenshot #22: Security Report**

50. Create your report:
```bash
cd ~/LabM4_weather_station/student_work
nano security_report.md
```

51. Use this template:
```markdown
# Security Assessment Report
Student: [Your Name]
Date: [Current Date]

## Executive Summary
Initial Score: X%
Final Score: Y%
Vulnerabilities Fixed: Z

## Vulnerabilities Found and Fixed

### 1. SQL Injection
- **Location**: weather_station.py, line XX
- **Severity**: Critical
- **Fix Applied**: Parameterized queries
- **Test Result**: Passed

### 2. Hardcoded Credentials
- **Location**: Multiple files
- **Severity**: High
- **Fix Applied**: Environment variables
- **Test Result**: Passed

[Continue for all vulnerabilities...]

## Lessons Learned
[Your reflection on what you learned]
```
52. **📸 Screenshot: Show your completed security report**

---

## 🎯 PART 7: Submission Package

### Step 7.1: Create Submission Archive

**Take Screenshot #23: Submission Package**

53. Create your submission:
```bash
cd ~/LabM4_weather_station
mkdir -p ~/submission_[YourLastName]
cp -r student_work/* ~/submission_[YourLastName]/
cp final_results.txt ~/submission_[YourLastName]/
cp .student_profile ~/submission_[YourLastName]/
```

54. Create archive:
```bash
cd ~
tar -czf [YourLastName]_Module4_Submission.tar.gz submission_[YourLastName]/
ls -la [YourLastName]_Module4_Submission.tar.gz
```
55. **📸 Screenshot: Show the created submission file with size**

### Step 7.2: Download Your Submission

56. Download to your computer:
```bash
# On your computer (not Pi):
scp pi@[PI_IP]:~/[YourLastName]_Module4_Submission.tar.gz ./
```

---

## 🔄 PART 8: Reset for Next Student (Instructor Only)

### If You Need to Start Over

57. Reset your environment:
```bash
cd ~/LabM4_weather_station/setup
./setup/reset_lab.sh soft
```

### Complete Reset (removes everything):
```bash
./setup/reset_lab.sh hard
```

---

## 📸 Screenshot Checklist (23 Total)

### Setup (7 screenshots)
- [ ] 1. SSH connection successful
- [ ] 2. Installation starting
- [ ] 3. Installation complete
- [ ] 4. Student onboarding process
- [ ] 5. Personalized welcome message
- [ ] 6. Student profile contents
- [ ] 7. Quick reference card

### Exploration (3 screenshots)
- [ ] 8. Weather station running
- [ ] 9. Simulation test complete
- [ ] 10. Initial security score

### Vulnerability Discovery (5 screenshots)
- [ ] 11. Vulnerable version activated
- [ ] 12. Hardcoded passwords found
- [ ] 13. API keys/secrets found
- [ ] 14. SQL injection test
- [ ] 15. Progress tracking updated

### Fixing Vulnerabilities (3 screenshots)
- [ ] 16. Environment variable fix
- [ ] 17. SQL injection fix
- [ ] 18. Input validation added

### Testing (3 screenshots)
- [ ] 19. Improved security score
- [ ] 20. SQL injection prevented
- [ ] 21. Final security score

### Documentation (2 screenshots)
- [ ] 22. Security report completed
- [ ] 23. Submission package created

---

## 📝 Grading Rubric

### Screenshots (23 points)
- 1 point per required screenshot

### Security Fixes (40 points)
- SQL Injection fixed: 10 points
- Hardcoded credentials removed: 10 points
- Input validation added: 10 points
- Additional vulnerabilities fixed: 10 points

### Documentation (20 points)
- Security report completeness: 10 points
- Code quality and comments: 10 points

### Testing (17 points)
- Initial test run: 5 points
- Final test improvement: 12 points

**Total: 100 points**

### Grade Scale
- A: 90-100 points
- B: 80-89 points
- C: 70-79 points
- D: 60-69 points
- F: Below 60 points

---

## ⚠️ Common Issues & Solutions

### Can't SSH to Pi?
```bash
# Ask instructor for:
1. Pi IP address
2. Password if changed from default
```

### Installation Failed?
```bash
# Try manual installation:
git clone https://github.com/kodkal/LabM4_weather_station.git
cd LabM4_weather_station
./setu./setup/quick_setup.sh
```

### Security Test Not Working?
```bash
# Make sure weather station is running:
# Terminal 1: ./start_weather_station.sh
# Terminal 2: ./test_security.sh
```

### Lost Your Work?
```bash
# Your work is saved in:
cd ~/LabM4_weather_station/student_work/
ls -la
```

---

## 🆘 Getting Help

### During Lab Hours
- Raise your hand for instructor assistance
- Check with classmates (collaboration is encouraged!)
- Review the quick reference: `cat student_work/quick_reference.txt`

### Outside Lab Hours
- Email instructor with:
  - Your name and student ID
  - Screenshot of the error
  - What step you're on
  - What you've tried

---

## 🏁 Final Checklist Before Submission

- [ ] All 23 screenshots taken and labeled
- [ ] Security score improved from initial test
- [ ] At least 5 vulnerabilities fixed
- [ ] Security report completed
- [ ] Submission archive created
- [ ] File downloaded to your computer

---

## 💡 Tips for Success

1. **Take screenshots as you go** - Don't wait until the end!
2. **Read error messages** - They often tell you exactly what's wrong
3. **Use the simulation mode** - No hardware needed!
4. **Test frequently** - Run `./test_security.sh` after each fix
5. **Document everything** - Update progress.md as you work
6. **Ask for help** - Don't struggle alone for too long

---

## 🎯 Learning Objectives

By completing this lab, you will:
- ✅ Understand common IoT security vulnerabilities
- ✅ Know how to identify security flaws in code
- ✅ Implement secure coding practices
- ✅ Test and verify security improvements
- ✅ Document security assessments professionally

---

**Remember**: The goal is to LEARN about IoT security, not just get a grade. Take time to understand each vulnerability and why the fix works!

---

*Student Guide v2.0 | Module 4 - IoT Security | UVU*

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
├── weather_station.py  # Main application
├── sensor_module.py    # Sensor interface
├── security/           # Security modules
└── api/               # API implementation
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