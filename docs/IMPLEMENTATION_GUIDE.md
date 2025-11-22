# Implementation Guide: Secure Weather Station
## GitHub Repository Setup and Deployment

---

## Repository Structure

```
secure-weather-station/
├── .github/
│   ├── workflows/
│   │   └── security-scan.yml      # Automated security scanning
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── security_vulnerability.md
├── weather_station.py         # Main application
├── sensor_module.py           # Sensor interfaces
├── security/                  # Security modules
│   ├── __init__.py
│   ├── auth.py               # JWT authentication
│   ├── encryption.py         # Data encryption
│   ├── validation.py         # Input validation
│   └── credentials.py        # Secure storage
├── api/                      # API implementation
│   ├── __init__.py
│   ├── server.py
│   └── routes.py
└── config/                   # Configuration
│       ├── __init__.py
│       └── settings.py
├── setup/                        # Setup scripts
│   ├── install.sh               # Automated installation
│   ├── secure_boot_setup.sh    # Secure boot configuration
│   ├── generate_certs.sh       # Certificate generation
│   └── create_service.sh       # Systemd service setup
├── tests/                       # Test suite
│   ├── test_security.py
│   ├── test_api.py
│   ├── test_sensors.py
│   └── test_validation.py
├── docs/                        # Documentation
│   ├── INSTRUCTOR_GUIDE.md
│   ├── STUDENT_GUIDE.md
│   ├── SECURITY_DESIGN.md
│   ├── THREAT_MODEL.md
│   ├── API_DOCUMENTATION.md
│   └── SETUP_GUIDE.md
├── scripts/                     # Utility scripts
│   ├── security_audit.py       # Security audit tool
│   ├── stress_test.py         # Load testing
│   └── backup.sh              # Backup script
├── docker/                     # Docker support
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example               # Environment variables template
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
├── README.md                 # Project overview
├── LICENSE                   # License file
├── SECURITY.md              # Security policy
└── CONTRIBUTING.md          # Contribution guidelines
```

---

## Quick Start Guide

### 1. Fork and Clone Repository

#### For Instructors:
```bash
# Create main repository
git init secure-weather-station
cd secure-weather-station

# Add all files
git add .
git commit -m "Initial commit: Secure Weather Station project"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/secure-weather-station.git
git push -u origin main

# Create instructor branch with solutions
git checkout -b instructor-solutions
# Add complete solutions
git push origin instructor-solutions

# Create student template branch
git checkout main
git checkout -b student-template
# Remove solutions, leave structure
git push origin student-template
```

#### For Students:
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/secure-weather-station.git
cd secure-weather-station

# Add upstream remote for updates
git remote add upstream https://github.com/INSTRUCTOR_USERNAME/secure-weather-station.git

# Create your working branch
git checkout -b development
```

### 2. Automated Installation

Create and run the installation script:

```bash
#!/bin/bash
# setup/install.sh

set -e  # Exit on error

echo "==================================="
echo "Secure Weather Station Installation"
echo "==================================="

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    i2c-tools \
    python3-smbus \
    libssl-dev \
    libffi-dev \
    build-essential \
    ufw

# Enable I2C interface
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p keys logs data data_backup

# Set permissions
echo "Setting secure permissions..."
chmod 700 keys
chmod 755 logs data
chmod 600 .env 2>/dev/null || true

# Generate initial certificates
echo "Generating self-signed certificates..."
./setup/generate_certs.sh

# Configure firewall
echo "Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8443/tcp comment 'Weather Station API'
sudo ufw --force enable

# Create systemd service
echo "Setting up systemd service..."
./setup/create_service.sh

echo "==================================="
echo "Installation Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Connect your sensor hardware"
echo "2. Configure settings in config/settings.py"
echo "3. Test with: python weather_station.py"
echo "4. Start service: sudo systemctl start weather-station"
echo ""
```

### 3. Certificate Generation Script

```bash
#!/bin/bash
# setup/generate_certs.sh

CERT_DIR="keys"
DAYS_VALID=365

# Create certificate directory
mkdir -p $CERT_DIR

# Generate private key
openssl genrsa -out $CERT_DIR/private.key 4096

# Generate certificate signing request
openssl req -new -key $CERT_DIR/private.key -out $CERT_DIR/request.csr -subj "/C=US/ST=Utah/L=Provo/O=UVU IoT Lab/CN=weather-station.local"

# Generate self-signed certificate
openssl x509 -req -days $DAYS_VALID -in $CERT_DIR/request.csr -signkey $CERT_DIR/private.key -out $CERT_DIR/certificate.crt

# Generate Diffie-Hellman parameters (for perfect forward secrecy)
openssl dhparam -out $CERT_DIR/dhparam.pem 2048

# Set secure permissions
chmod 600 $CERT_DIR/private.key
chmod 644 $CERT_DIR/certificate.crt
chmod 644 $CERT_DIR/dhparam.pem

echo "Certificates generated successfully in $CERT_DIR/"
```

---

## Configuration Management

### 1. Environment Variables (.env.example)

```bash
# Security Configuration
SECRET_KEY=generate-a-secure-random-key-here
JWT_SECRET=another-secure-random-key
ENCRYPTION_KEY=base64-encoded-fernet-key

# Device Configuration
DEVICE_ID=weather-station-001
LOCATION=UVU-Lab-Room-101

# Sensor Configuration
SENSOR_TYPE=BME280
SENSOR_PIN=4
READING_INTERVAL=60

# API Configuration
API_PORT=8443
API_HOST=0.0.0.0
DEBUG=False

# Database Configuration
DB_PATH=data/weather.db
CREDENTIAL_DB=data/credentials.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/weather_station.log

# Certificate Paths
CERT_FILE=keys/certificate.crt
PRIVATE_KEY_FILE=keys/private.key
CA_CERT_FILE=keys/ca.crt
```

### 2. Settings Module (config/settings.py)

```python
"""
Configuration Settings for Secure Weather Station
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'development-only-key')
JWT_SECRET = os.environ.get('JWT_SECRET', SECRET_KEY)
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

# Validate security keys in production
if not os.environ.get('DEBUG', 'False') == 'True':
    if SECRET_KEY == 'development-only-key':
        raise ValueError("SECRET_KEY must be set in production")

# Device Settings
DEVICE_ID = os.environ.get('DEVICE_ID', 'weather-001')
LOCATION = os.environ.get('LOCATION', 'Unknown')

# Sensor Settings
SENSOR_TYPE = os.environ.get('SENSOR_TYPE', 'BME280')
SENSOR_PIN = int(os.environ.get('SENSOR_PIN', '4'))
READING_INTERVAL = int(os.environ.get('READING_INTERVAL', '60'))

# API Settings
API_PORT = int(os.environ.get('API_PORT', '8443'))
API_HOST = os.environ.get('API_HOST', '0.0.0.0')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Certificate Settings
CERT_FILE = os.path.join(BASE_DIR, os.environ.get('CERT_FILE', 'keys/certificate.crt'))
PRIVATE_KEY_FILE = os.path.join(BASE_DIR, os.environ.get('PRIVATE_KEY_FILE', 'keys/private.key'))
CA_CERT_FILE = os.path.join(BASE_DIR, os.environ.get('CA_CERT_FILE', 'keys/ca.crt'))
KEY_FILE = os.path.join(BASE_DIR, 'keys/master.key')

# Database Settings
DB_PATH = os.path.join(BASE_DIR, os.environ.get('DB_PATH', 'data/weather.db'))
CREDENTIAL_DB = os.path.join(BASE_DIR, os.environ.get('CREDENTIAL_DB', 'data/credentials.db'))

# Logging Settings
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, os.environ.get('LOG_FILE', 'logs/weather_station.log'))
```

---

## Deployment Options

### Option 1: Systemd Service (Recommended for Production)

```bash
#!/bin/bash
# setup/create_service.sh

SERVICE_FILE="/etc/systemd/system/weather-station.service"
PROJECT_DIR=$(pwd)
USER=$(whoami)

# Create service file
sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Secure Weather Station IoT Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/weather_station.py
Restart=on-failure
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR/logs $PROJECT_DIR/data

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable weather-station.service

echo "Service created. Commands:"
echo "  Start:   sudo systemctl start weather-station"
echo "  Stop:    sudo systemctl stop weather-station"
echo "  Status:  sudo systemctl status weather-station"
echo "  Logs:    sudo journalctl -u weather-station -f"
```

### Option 2: Docker Deployment

```dockerfile
# docker/Dockerfile
FROM python:3.9-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p keys logs data

# Create non-root user
RUN useradd -m -u 1000 weather && chown -R weather:weather /app
USER weather

# Expose API port
EXPOSE 8443

# Run the application
CMD ["python", "weather_station.py"]
```

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  weather-station:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: secure-weather-station
    restart: unless-stopped
    ports:
      - "8443:8443"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./keys:/app/keys:ro
    environment:
      - DEVICE_ID=docker-weather-001
      - SENSOR_TYPE=SIMULATED
      - DEBUG=False
    networks:
      - weather-net
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp

networks:
  weather-net:
    driver: bridge
```

### Option 3: Development Mode

```bash
# For development and testing
#!/bin/bash
# scripts/run_dev.sh

# Activate virtual environment
source venv/bin/activate

# Set development environment
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with auto-reload
watchmedo auto-restart \
    --patterns="*.py" \
    --recursive \
    --signal SIGTERM \
    python weather_station.py
```

---

## Testing Infrastructure

### 1. Automated Security Testing

```python
#!/usr/bin/env python3
# scripts/security_audit.py

"""
Automated Security Audit for Weather Station
"""

import sys
import os
import subprocess
import json
from pathlib import Path

class SecurityAuditor:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
    
    def audit_file_permissions(self):
        """Check critical file permissions"""
        critical_files = {
            'keys/private.key': 0o600,
            'keys/master.key': 0o600,
            '.env': 0o600,
            'data/credentials.db': 0o600
        }
        
        for filepath, expected_mode in critical_files.items():
            if os.path.exists(filepath):
                actual_mode = os.stat(filepath).st_mode & 0o777
                if actual_mode != expected_mode:
                    self.issues.append(
                        f"Insecure permissions on {filepath}: "
                        f"{oct(actual_mode)} (expected {oct(expected_mode)})"
                    )
                else:
                    self.passed.append(f"✓ {filepath} permissions correct")
    
    def audit_dependencies(self):
        """Check for known vulnerabilities in dependencies"""
        try:
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True
            )
            
            vulnerabilities = json.loads(result.stdout)
            if vulnerabilities:
                for vuln in vulnerabilities:
                    self.issues.append(
                        f"Vulnerability in {vuln['package']}: {vuln['vulnerability']}"
                    )
            else:
                self.passed.append("✓ No known vulnerabilities in dependencies")
        except Exception as e:
            self.warnings.append(f"Could not check dependencies: {e}")
    
    def audit_code_security(self):
        """Static code analysis for security issues"""
        try:
            result = subprocess.run(
                ['bandit', '-r', 'src', '-f', 'json'],
                capture_output=True,
                text=True
            )
            
            findings = json.loads(result.stdout)
            for issue in findings.get('results', []):
                if issue['issue_severity'] in ['MEDIUM', 'HIGH']:
                    self.issues.append(
                        f"Security issue in {issue['filename']}: "
                        f"{issue['issue_text']}"
                    )
        except Exception as e:
            self.warnings.append(f"Could not analyze code: {e}")
    
    def audit_ssl_certificates(self):
        """Check SSL certificate validity"""
        cert_file = 'keys/certificate.crt'
        if os.path.exists(cert_file):
            try:
                result = subprocess.run(
                    ['openssl', 'x509', '-in', cert_file, '-noout', '-dates'],
                    capture_output=True,
                    text=True
                )
                
                if 'notAfter' in result.stdout:
                    self.passed.append("✓ SSL certificate is valid")
                else:
                    self.issues.append("SSL certificate validation failed")
            except Exception as e:
                self.warnings.append(f"Could not check certificate: {e}")
    
    def run_audit(self):
        """Run complete security audit"""
        print("Running Security Audit...")
        print("=" * 50)
        
        self.audit_file_permissions()
        self.audit_dependencies()
        self.audit_code_security()
        self.audit_ssl_certificates()
        
        # Report results
        if self.passed:
            print("\n✅ PASSED CHECKS:")
            for item in self.passed:
                print(f"  {item}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.issues:
            print("\n❌ SECURITY ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
            return 1
        else:
            print("\n✅ No critical security issues found!")
            return 0

if __name__ == "__main__":
    auditor = SecurityAuditor()
    sys.exit(auditor.run_audit())
```

### 2. GitHub Actions Security Workflow

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [ main, development ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install safety bandit pytest-cov
    
    - name: Run Safety check
      run: safety check --json
      continue-on-error: true
    
    - name: Run Bandit security linter
      run: bandit -r src -f json -o bandit-report.json
    
    - name: Run tests with coverage
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
    
    - name: Check for secrets
      uses: trufflesecurity/trufflehog@main
      with:
        path: ./
```

---

## Maintenance and Updates

### Regular Maintenance Tasks

```bash
#!/bin/bash
# scripts/maintenance.sh

echo "Running maintenance tasks..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
source venv/bin/activate
pip list --outdated
pip install --upgrade -r requirements.txt

# Rotate logs
sudo logrotate -f /etc/logrotate.d/weather-station

# Backup data
./scripts/backup.sh

# Run security audit
python scripts/security_audit.py

# Check certificate expiration
openssl x509 -in keys/certificate.crt -noout -checkend 2592000
if [ $? -eq 0 ]; then
    echo "Certificate valid for more than 30 days"
else
    echo "WARNING: Certificate expires within 30 days!"
fi

echo "Maintenance complete"
```

### Backup Strategy

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/home/pi/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="weather_station_backup_${TIMESTAMP}.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    data/ \
    logs/ \
    keys/ \
    config/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "weather_station_backup_*.tar.gz" -mtime +7 -delete

echo "Backup created: $BACKUP_DIR/$BACKUP_FILE"
```

---

## Instructor Repository Management

### Branch Strategy

```bash
# Main branch - stable release for students
main/
  - Complete project structure
  - Starter code with TODOs
  - All documentation
  - Tests (without solutions)

# Instructor-solutions branch - complete implementation
instructor-solutions/
  - Full working code
  - Complete test suite
  - Grading scripts
  - Answer keys

# Student-template branch - minimal starter
student-template/
  - Project structure only
  - Empty implementation files
  - Documentation
  - Test cases

# Development branch - ongoing improvements
development/
  - New features
  - Bug fixes
  - Documentation updates
```

### Release Process

```bash
#!/bin/bash
# scripts/prepare_release.sh

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./prepare_release.sh <version>"
    exit 1
fi

# Update version in files
sed -i "s/Version: .*/Version: $VERSION/" README.md
sed -i "s/__version__ = .*/__version__ = '$VERSION'/" src/__init__.py

# Create release branch
git checkout -b release/$VERSION

# Run tests
pytest tests/

# Run security audit
python scripts/security_audit.py

# Create tag
git tag -a v$VERSION -m "Release version $VERSION"

# Push to repository
git push origin release/$VERSION
git push origin v$VERSION

echo "Release $VERSION prepared"
```

---

## Support Resources

### For Instructors
- Private instructor repository with solutions
- Slack channel for instructor support
- Regular update meetings
- Grading automation scripts

### For Students
- Public discussion forum
- Office hours schedule
- Video tutorials
- Sample implementations

### Documentation
- API documentation with Swagger
- Security best practices guide
- Troubleshooting handbook
- Performance optimization guide

---

## Contributing Guidelines

### For Students
1. Fork the repository
2. Create feature branch
3. Implement changes
4. Write tests
5. Submit pull request

### Code Standards
- Follow PEP 8
- Add docstrings
- Write unit tests
- Update documentation
- No hardcoded secrets

### Security Requirements
- All PRs must pass security scan
- No known vulnerabilities
- Proper input validation
- Secure coding practices

---

## License

This project is licensed under the MIT License for educational use.

---

## Contact

**Instructor**: [Your Name]  
**Email**: [instructor@university.edu]  
**GitHub**: [github.com/username]  
**Office Hours**: [Schedule]

---

*Implementation Guide v1.0 | November 2024*