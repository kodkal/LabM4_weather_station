# 🔐 Secure Weather Station - IoT Security Project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4%20%7C%203B%2B-red.svg)](https://www.raspberrypi.org/)

## 📋 Overview

A comprehensive IoT security education project for Utah Valley University's IoT Security course. Students build a functional weather monitoring station while implementing industry-standard security controls including secure boot, encrypted communications, JWT authentication, input validation, and secure credential storage.

### 🎓 No Sensors? No Problem!
**This project includes a comprehensive simulation mode** that allows you to complete all assignments without physical sensors. The simulator generates realistic weather data with patterns, anomalies, and smooth transitions. All security features work identically with simulated or real sensor data.

### 🎯 Learning Objectives
- Implement secure boot processes and integrity checking
- Deploy TLS/SSL encryption for data transmission
- Design JWT-based authentication systems
- Prevent injection attacks through input validation
- Manage credentials with secure storage and rotation

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi 4 (2GB+) or 3B+ **OR** any computer for simulation mode
- BME280 or DHT22 sensor **OPTIONAL** - simulation mode available
- Python 3.9+
- Basic Linux command line knowledge

### Installation

#### Option 1: With Physical Sensors
```bash
# Clone the repository
git clone https://github.com/yourusername/secure-weather-station.git
cd secure-weather-station

# Run automated installation
chmod +x setup/install.sh
./setup/install.sh

# Configure your settings
cp .env.example .env
nano .env  # Set SENSOR_TYPE=AUTO

# Run the weather station
python src/weather_station.py
```

#### Option 2: Simulation Mode (No Sensors Required!)
```bash
# Clone the repository
git clone https://github.com/yourusername/secure-weather-station.git
cd secure-weather-station

# Install dependencies
pip install -r requirements.txt

# Enable simulation mode
export SENSOR_SIMULATION=true

# Run the weather station
python src/weather_station.py

# Test simulation features
python scripts/test_simulation.py
```

## 📁 Project Structure

```
secure-weather-station/
├── src/                    # Source code
│   ├── weather_station.py  # Main application
│   ├── sensor_module.py    # Sensor interfaces
│   ├── security/           # Security modules (auth, encryption, validation)
│   └── api/               # RESTful API implementation
├── docs/                  # Documentation
│   ├── INSTRUCTOR_GUIDE.md
│   ├── STUDENT_GUIDE.md
│   └── IMPLEMENTATION_GUIDE.md
├── setup/                 # Setup scripts
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## 🔒 Security Features

### Implemented Security Controls

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **Secure Boot** | Integrity verification at startup | Hash validation of critical files |
| **Data Encryption** | TLS/SSL for all transmissions | AES-256, RSA, Fernet encryption |
| **Authentication** | JWT token-based API access | Token generation, validation, refresh |
| **Input Validation** | Injection attack prevention | Regex patterns, whitelisting |
| **Credential Storage** | Encrypted credential management | Argon2 hashing, encrypted database |
| **Rate Limiting** | DDoS protection | Per-IP request limits |
| **Audit Logging** | Security event tracking | JSON structured logging |

## 🛠️ Hardware Setup

### 💻 Simulation Mode (No Hardware Required!)
```bash
# Run without any sensors - perfect for development and learning
export SENSOR_SIMULATION=true
python src/weather_station.py

# Or configure in .env file
SENSOR_TYPE=SIMULATED
SIMULATION_LOCATION=utah
```
See [Simulation Guide](SIMULATION_GUIDE.md) for details.

### Wiring Diagram - BME280 (I2C)
```
BME280      →  Raspberry Pi
VCC         →  Pin 1 (3.3V)
GND         →  Pin 6 (Ground)
SCL         →  Pin 5 (GPIO3)
SDA         →  Pin 3 (GPIO2)
```

### Wiring Diagram - DHT22
```
DHT22       →  Raspberry Pi
VCC         →  Pin 2 (5V)
Data        →  Pin 7 (GPIO4)
GND         →  Pin 6 (Ground)
```

## 📡 API Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/status` | System status | Optional |
| GET | `/api/data` | Current sensor data | Required |
| GET | `/api/history` | Historical data | Required |
| POST | `/api/auth/login` | Authenticate | None |
| POST | `/api/auth/refresh` | Refresh token | Required |

### Example API Usage

```bash
# Authenticate
curl -X POST https://localhost:8443/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"device_id": "weather-001", "api_key": "your-key"}'

# Get sensor data
curl -X GET https://localhost:8443/api/data \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run security audit
python scripts/security_audit.py

# Run specific test categories
pytest tests/test_security.py
pytest tests/test_validation.py
```

## 📊 Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Sensor Read Time | < 100ms | ~50ms |
| Encryption Overhead | < 10ms | ~5ms |
| API Response Time | < 200ms | ~150ms |
| JWT Validation | < 5ms | ~2ms |

## 📚 Documentation

### For Instructors
- [Instructor Guide](INSTRUCTOR_GUIDE.md) - Teaching notes, grading rubrics, lab sessions
- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Repository setup, deployment options

### For Students
- [Student Guide](STUDENT_GUIDE.md) - Step-by-step instructions, troubleshooting
- [Security Design Template](SECURITY_DESIGN.md) - Document template
- [Threat Model Template](THREAT_MODEL.md) - Threat analysis template

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Sensor not detected | Check wiring, enable I2C with `raspi-config` |
| Permission denied | Add user to gpio group: `sudo usermod -a -G gpio $USER` |
| Certificate errors | Regenerate certificates: `./setup/generate_certs.sh` |
| JWT token invalid | Check system time: `date` |

## 🤝 Contributing

We welcome contributions!

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run in development mode
export DEBUG=True
python src/weather_station.py
```

## 📈 Project Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Foundation & Secure Boot | Hardened Pi, Boot verification |
| 2 | Encryption & Communication | TLS setup, Encrypted transmission |
| 3 | Authentication & API | JWT implementation, API endpoints |
| 4 | Validation & Storage | Input validation, Secure storage |

## 🏆 Grading Criteria

- **Implementation** (40%): Working security features
- **Documentation** (25%): Security design document
- **Threat Model** (20%): Comprehensive threat analysis
- **Code Quality** (10%): Clean, documented code
- **Testing** (5%): Security testing evidence

## 📖 Resources

### Essential Reading
- [OWASP IoT Top 10](https://owasp.org/www-project-internet-of-things/)
- [JWT Best Practices](https://jwt.io/introduction)
- [Raspberry Pi Security Guide](https://www.raspberrypi.org/documentation/configuration/security.md)

### Tools
- **Wireshark**: Network traffic analysis
- **Postman**: API testing
- **OWASP ZAP**: Security scanning

## 👥 Team

**Course Instructor**: [Your Name]  
**University**: Utah Valley University  
**Department**: Computer Science  
**Course**: IoT Security

## 📄 License

This project is licensed under the MIT License

## 🙏 Acknowledgments

- Utah Valley University Computer Science Department
- Raspberry Pi Foundation
- OWASP IoT Security Project
- Open source security community

## ⚠️ Security Disclosure

Found a security issue? Please email security@[yourdomain] instead of using the issue tracker.

## 📞 Support

- **Instructor Email**: instructor@uvu.edu
- **Office Hours**: MW 2-4 PM
- **Course Forum**: [link]
- **Slack Channel**: #iot-security

---

### ⭐ Star this repository if you find it helpful!

**Last Updated**: November 2024  
**Version**: 1.0.0  
**Status**: Active Development

---

<p align="center">
  Made with ❤️ for IoT Security Education
</p>