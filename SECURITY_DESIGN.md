# Security Design Document
## Weather Station IoT Security Architecture

---

### Document Information
- **Student Name**: [Your Name]
- **Student ID**: [Your Student ID]
- **Date**: [Current Date]
- **Version**: 1.0
- **Module**: IoT Security - Module 4

---

## 1. Executive Summary

### 1.1 Purpose
[Describe the purpose of this security design document in 2-3 sentences]

### 1.2 Scope
This document covers the security architecture for:
- [ ] Weather Station hardware
- [ ] Sensor data collection
- [ ] Data transmission
- [ ] API endpoints
- [ ] Credential management
- [ ] User authentication

### 1.3 Security Objectives
1. **Confidentiality**: [How you ensure data privacy]
2. **Integrity**: [How you ensure data hasn't been tampered with]
3. **Availability**: [How you ensure system remains accessible]
4. **Non-repudiation**: [How you ensure actions can be traced]

---

## 2. System Architecture

### 2.1 Component Diagram
```
[Raspberry Pi] --> [Sensors]
       |
       v
[Weather Station App]
       |
    +--+--+
    |     |
    v     v
[API]   [Database]
    |
    v
[Client/User]
```

### 2.2 Components

#### 2.2.1 Hardware Layer
- **Raspberry Pi 4**: [Describe role]
- **BME280/DHT22 Sensor**: [Describe role]
- **Network Interface**: [Ethernet/WiFi]

#### 2.2.2 Application Layer
- **Main Application** (`weather_station.py`): [Describe functionality]
- **Sensor Module** (`sensor_module.py`): [Describe functionality]
- **Security Modules**: [List and describe each]

#### 2.2.3 Data Layer
- **Local Storage**: [Describe what's stored locally]
- **Database**: [Describe database usage]
- **Log Files**: [Describe logging approach]

---

## 3. Security Controls Implementation

### 3.1 Authentication & Authorization

#### 3.1.1 Current Implementation
- **Method Used**: [JWT/Session/API Key]
- **Token Expiration**: [Duration]
- **Refresh Strategy**: [How tokens are refreshed]

#### 3.1.2 Code Example
```python
# Example of your authentication implementation
[Insert your actual authentication code here]
```

#### 3.1.3 Improvements Made
- [ ] Removed hardcoded credentials
- [ ] Implemented secure token generation
- [ ] Added token expiration
- [ ] Other: [Specify]

### 3.2 Data Encryption

#### 3.2.1 Encryption at Rest
- **Method**: [AES/Fernet/Other]
- **Key Length**: [128/256 bits]
- **Key Storage**: [How keys are stored]

#### 3.2.2 Encryption in Transit
- **Protocol**: [TLS/SSL version]
- **Certificate Type**: [Self-signed/CA-signed]
- **Cipher Suite**: [Which ciphers are used]

#### 3.2.3 Code Example
```python
# Example of your encryption implementation
[Insert your actual encryption code here]
```

### 3.3 Input Validation

#### 3.3.1 Validation Strategy
- **Approach**: [Whitelist/Blacklist]
- **Validation Points**: [Where validation occurs]
- **Sanitization Method**: [How input is cleaned]

#### 3.3.2 Validation Rules
| Input Type | Validation Rule | Example |
|------------|----------------|---------|
| Username | Alphanumeric only, 3-20 chars | `^[a-zA-Z0-9]{3,20}$` |
| Temperature | Float, -50 to 60 | `-50.0 <= value <= 60.0` |
| Device ID | UUID format | `[0-9a-f]{8}-[0-9a-f]{4}-...` |
| [Add more] | | |

#### 3.3.3 Code Example
```python
# Example of your input validation
[Insert your actual validation code here]
```

### 3.4 Secure Boot Process

#### 3.4.1 Boot Verification Steps
1. [First verification step]
2. [Second verification step]
3. [Additional steps]

#### 3.4.2 Integrity Checks
- **Files Checked**: [List critical files]
- **Hash Algorithm**: [SHA256/SHA512]
- **Verification Frequency**: [On boot/Periodic]

### 3.5 Credential Management

#### 3.5.1 Storage Method
- **Location**: [Where credentials are stored]
- **Encryption**: [How they're encrypted]
- **Access Control**: [Who can access]

#### 3.5.2 Environment Variables
```bash
# Example .env configuration
SECRET_KEY=[Describe how generated]
JWT_SECRET=[Describe how generated]
API_KEY=[Describe how managed]
```

### 3.6 Logging & Monitoring

#### 3.6.1 Security Events Logged
- [ ] Authentication attempts
- [ ] Authorization failures
- [ ] Input validation failures
- [ ] System errors
- [ ] Configuration changes
- [ ] Other: [Specify]

#### 3.6.2 Log Format
```json
{
    "timestamp": "2024-XX-XX HH:MM:SS",
    "event": "authentication_failed",
    "user": "username",
    "ip_address": "192.168.1.100",
    "details": "Invalid password"
}
```

---

## 4. Security Testing

### 4.1 Vulnerabilities Found

| # | Vulnerability | Severity | Location | Status |
|---|--------------|----------|----------|---------|
| 1 | SQL Injection | Critical | `/api/login` | Fixed ✓ |
| 2 | Hardcoded Credentials | High | `weather_station.py:45` | Fixed ✓ |
| 3 | No Input Validation | High | Multiple locations | Fixed ✓ |
| 4 | Weak Encryption | Medium | `encryption.py` | Fixed ✓ |
| 5 | [Add more] | | | |

### 4.2 Testing Results

#### 4.2.1 Initial Security Score
```
Date: [Date]
Score: [X]%
Grade: [F/D/C/B/A]
Failed Tests: [List]
```

#### 4.2.2 Final Security Score
```
Date: [Date]
Score: [Y]%
Grade: [F/D/C/B/A]
Passed Tests: [List]
```

### 4.3 Test Evidence
[Reference your screenshot numbers here]
- Screenshot #10: Initial security test showing failures
- Screenshot #21: Final security test showing improvements

---

## 5. Compliance & Standards

### 5.1 Standards Followed
- [ ] OWASP IoT Top 10
- [ ] NIST IoT Security Guidelines
- [ ] Industry best practices
- [ ] Course requirements

### 5.2 Security Principles Applied
- [ ] **Least Privilege**: Users only get minimum required access
- [ ] **Defense in Depth**: Multiple layers of security
- [ ] **Fail Secure**: System fails to a secure state
- [ ] **Separation of Concerns**: Security isolated in modules
- [ ] **Minimize Attack Surface**: Removed unnecessary features

---

## 6. Known Limitations

### 6.1 Current Limitations
1. [Limitation 1 and why it exists]
2. [Limitation 2 and why it exists]
3. [Limitation 3 and why it exists]

### 6.2 Acceptable Risks
| Risk | Justification | Mitigation |
|------|--------------|------------|
| Self-signed certificates | Educational environment | Would use CA in production |
| [Add more] | | |

---

## 7. Future Improvements

### 7.1 Short-term (Could implement now)
- [ ] [Improvement 1]
- [ ] [Improvement 2]
- [ ] [Improvement 3]

### 7.2 Long-term (Production requirements)
- [ ] [Improvement 1]
- [ ] [Improvement 2]
- [ ] [Improvement 3]

---

## 8. Conclusion

### 8.1 Security Posture Assessment
[Provide your assessment of the current security posture in 3-4 sentences]

### 8.2 Lessons Learned
1. [Key learning 1]
2. [Key learning 2]
3. [Key learning 3]

### 8.3 Real-world Application
[Describe how these security measures would apply to actual IoT deployments]

---

## Appendices

### Appendix A: Code Snippets
[Include relevant code snippets not shown above]

### Appendix B: Configuration Files
[Include relevant configuration examples]

### Appendix C: Test Results
[Include detailed test output]

### Appendix D: References
1. OWASP IoT Top 10: https://owasp.org/www-project-internet-of-things/
2. NIST IoT Security: https://www.nist.gov/topics/internet-things-iot
3. [Add more references you used]

---

## Approval

**Student Signature**: _______________________  
**Date**: _______________________

**Instructor Review**: _______________________  
**Grade**: _______________________

---

*Security Design Document v1.0 | Module 4 - IoT Security | UVU*