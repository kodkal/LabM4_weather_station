# Instructor Guide: Secure Weather Station Project
## Module 4 - IoT Security Course | UVU

---

## Table of Contents
1. [Course Overview](#course-overview)
2. [Learning Objectives](#learning-objectives)
3. [Prerequisites & Setup](#prerequisites--setup)
4. [Teaching Schedule](#teaching-schedule)
5. [Key Security Concepts](#key-security-concepts)
6. [Lab Sessions](#lab-sessions)
7. [Assessment & Grading](#assessment--grading)
8. [Common Issues & Solutions](#common-issues--solutions)
9. [Discussion Topics](#discussion-topics)
10. [Additional Resources](#additional-resources)

---

## Course Overview

### Project Summary
The Secure Weather Station project is designed to teach students practical IoT security through hands-on implementation. Students will build a functional weather monitoring system while implementing industry-standard security controls.

### Teaching Philosophy
- **Learn by Doing**: Students implement real security controls
- **Defense in Depth**: Multiple layers of security
- **Fail Safely**: Understanding security failures and recovery
- **Industry Relevance**: Using current security standards and practices

### Time Commitment
- **Total Duration**: 4 weeks (recommended)
- **Class Time**: 3 hours/week
- **Lab Time**: 2-3 hours/week
- **Outside Work**: 3-5 hours/week

---

## Learning Objectives

### Primary Objectives
By completing this module, students will be able to:

1. **Implement Secure Boot Processes**
   - Understand boot security principles
   - Implement integrity checking
   - Configure secure boot parameters

2. **Deploy Encrypted Communications**
   - Implement TLS/SSL for data transmission
   - Understand certificate management
   - Apply encryption best practices

3. **Design Authentication Systems**
   - Implement JWT token authentication
   - Understand API security
   - Apply principle of least privilege

4. **Validate Input Data**
   - Prevent injection attacks
   - Implement data sanitization
   - Understand validation patterns

5. **Manage Credentials Securely**
   - Implement secure storage
   - Understand key management
   - Apply rotation policies

### Secondary Objectives
- Develop security documentation skills
- Perform threat modeling
- Conduct security testing
- Understand compliance requirements

---

## Prerequisites & Setup

### Student Prerequisites
- **Programming**: Intermediate Python (functions, classes, modules)
- **Linux**: Basic command line skills
- **Networking**: Understanding of HTTP, TCP/IP
- **Hardware**: Basic electronics knowledge helpful but not required

### Hardware Requirements (Per Student/Team)
```
Required:
- Raspberry Pi 4 (2GB+ RAM) or Pi 3B+
- MicroSD Card (16GB minimum, Class 10)
- Power Supply (5V, 3A for Pi 4)
- BME280 or DHT22 sensor
- Breadboard and jumper wires

Optional but Recommended:
- Case for Raspberry Pi
- Heat sinks
- HDMI cable and monitor (for initial setup)
- USB keyboard (for initial setup)
```

### Software Setup
```bash
# Initial Pi Setup (provide pre-configured images if possible)
1. Flash Raspberry Pi OS Lite
2. Enable SSH
3. Configure WiFi
4. Update system packages
5. Install Python 3.9+
6. Clone project repository
```

### Instructor Preparation
1. **Test Environment**: Set up a complete working example
2. **Network Setup**: Ensure lab network supports IoT devices
3. **Certificates**: Pre-generate CA certificates for the class
4. **Monitoring**: Set up centralized logging/monitoring server
5. **Backup Plans**: Have simulation mode ready for hardware failures

---

## Teaching Schedule

### Week 1: Foundation & Secure Boot
**Lecture Topics (1.5 hours)**
- IoT security landscape and threats
- Secure boot concepts and implementation
- Hardware security modules (TPM/HSM)
- File integrity monitoring

**Lab Activities (1.5 hours)**
- Raspberry Pi setup and hardening
- Implement secure boot checks
- Configure file integrity monitoring
- Create boot hash verification

**Assignment**
- Complete secure boot implementation
- Document security configurations
- Research: "Real-world IoT secure boot bypasses"

### Week 2: Encryption & Secure Communication
**Lecture Topics (1.5 hours)**
- Cryptography fundamentals for IoT
- TLS/SSL implementation
- Certificate management
- Encryption algorithms comparison

**Lab Activities (1.5 hours)**
- Generate SSL certificates
- Implement data encryption (AES, Fernet)
- Configure TLS communication
- Test encrypted data transmission

**Assignment**
- Implement complete encryption module
- Performance testing: encryption overhead
- Research: "IoT encryption standards comparison"

### Week 3: Authentication & Authorization
**Lecture Topics (1.5 hours)**
- Authentication methods for IoT
- JWT tokens and session management
- API security best practices
- Rate limiting and DDoS protection

**Lab Activities (1.5 hours)**
- Implement JWT authentication
- Create API with Flask
- Add rate limiting
- Test authentication flows

**Assignment**
- Complete API with authentication
- Penetration testing on peer's API
- Create API documentation

### Week 4: Input Validation & Secure Storage
**Lecture Topics (1.5 hours)**
- Common injection attacks in IoT
- Input validation strategies
- Secure credential storage
- Key management and rotation

**Lab Activities (1.5 hours)**
- Implement input validators
- Create secure credential store
- Test injection prevention
- Implement key rotation

**Assignment**
- Complete security implementation
- Create threat model document
- Present security design

---

## Key Security Concepts

### 1. Secure Boot Process
**Teaching Points:**
- Boot chain verification
- Measured boot vs. verified boot
- UEFI Secure Boot (conceptual)

**Demonstration Code:**
```python
# Show how to verify boot integrity
def verify_boot_integrity():
    """Demonstrate boot verification concept"""
    current_hash = calculate_boot_hash()
    stored_hash = get_stored_hash()
    
    if current_hash != stored_hash:
        log_security_event("Boot tampering detected!")
        enter_safe_mode()
    
    return current_hash == stored_hash
```

**Discussion Questions:**
- What happens if an attacker modifies boot files?
- How can we detect runtime modifications?
- What are the limitations of software-based secure boot?

### 2. Encryption Implementation
**Teaching Points:**
- Symmetric vs. asymmetric encryption
- Key derivation functions
- Hybrid encryption schemes

**Common Pitfalls to Address:**
- Hard-coded keys in source code
- Weak random number generation
- Improper key storage
- Not rotating keys

### 3. Authentication Security
**Teaching Points:**
- Token-based vs. session-based auth
- Stateless authentication benefits
- Token refresh strategies

**Live Coding Demo:**
```python
# Demonstrate JWT token validation
def validate_token_security(token):
    """Show common JWT security checks"""
    # 1. Signature verification
    # 2. Expiration check
    # 3. Issuer validation
    # 4. Audience check
    # 5. Replay attack prevention
```

### 4. Input Validation
**Teaching Points:**
- Whitelisting vs. blacklisting
- Regular expressions for validation
- SQL injection prevention
- Command injection prevention

**Interactive Exercise:**
Have students attempt to break each other's validation:
```python
# Challenge: Find the vulnerability
def unsafe_validation(user_input):
    if "DROP" not in user_input.upper():
        return True  # What's wrong with this?
```

---

## Lab Sessions

### Lab 1: Secure Setup
**Objectives:**
- Configure Raspberry Pi securely
- Implement SSH key authentication
- Set up firewall rules

**Checkpoints:**
- [ ] SSH key-only authentication enabled
- [ ] Firewall configured (ufw/iptables)
- [ ] Unnecessary services disabled
- [ ] Secure boot verification working

### Lab 2: Sensor Integration
**Objectives:**
- Connect and test sensors
- Implement data validation
- Add anomaly detection

**Checkpoints:**
- [ ] Sensor reading successfully
- [ ] Data validation working
- [ ] Anomaly detection triggers
- [ ] Error handling implemented

### Lab 3: Secure API Development
**Objectives:**
- Create RESTful API
- Implement authentication
- Add rate limiting

**Checkpoints:**
- [ ] API endpoints working
- [ ] JWT authentication required
- [ ] Rate limiting active
- [ ] HTTPS configured

### Lab 4: Security Testing
**Objectives:**
- Perform security audit
- Test injection prevention
- Verify encryption

**Checkpoints:**
- [ ] Injection attempts blocked
- [ ] Encryption verified with Wireshark
- [ ] Authentication bypass attempts failed
- [ ] Security audit passed

---

## Assessment & Grading

### Grading Rubric

#### Implementation (40%)
| Criteria | Excellent (A) | Good (B) | Satisfactory (C) | Needs Improvement (D) |
|----------|--------------|----------|------------------|----------------------|
| Secure Boot | Fully implemented with integrity checks | Basic implementation works | Partial implementation | Not implemented |
| Encryption | All data encrypted, proper key management | Data encrypted, basic key storage | Some encryption | Minimal encryption |
| Authentication | JWT + API keys + rate limiting | JWT working properly | Basic authentication | Weak/no authentication |
| Input Validation | Comprehensive validation, injection prevention | Good validation coverage | Some validation | Minimal validation |
| Credential Storage | Encrypted storage with rotation | Encrypted storage | Basic storage | Insecure storage |

#### Documentation (25%)
- Security Design Document (15%)
  - Architecture diagram
  - Security controls description
  - Implementation details
  - Testing procedures
  
- Code Documentation (10%)
  - Clear comments
  - Function documentation
  - README completeness

#### Threat Model (20%)
- Threat identification (10%)
- Mitigation strategies (10%)

#### Testing (10%)
- Unit tests for security functions
- Security testing evidence
- Peer testing participation

#### Presentation (5%)
- Clear explanation of security decisions
- Demonstration of working system
- Q&A handling

### Sample Test Questions

**Conceptual Questions:**
1. Explain the difference between encryption at rest and encryption in transit. How does this project implement both?
2. What is a JWT token and why is it suitable for IoT authentication?
3. Describe three types of injection attacks and how input validation prevents them.

**Practical Questions:**
1. Given this code snippet, identify the security vulnerability:
```python
def get_sensor_data(sensor_id):
    query = f"SELECT * FROM sensors WHERE id = {sensor_id}"
    return execute_query(query)
```

2. Write a function to validate an email address without using regex.

3. Design a key rotation strategy for IoT devices deployed in the field.

---

## Common Issues & Solutions

### Hardware Issues

**Issue: Sensor Not Detected**
```bash
# Diagnostic steps:
1. Check wiring connections
2. Verify I2C is enabled: sudo raspi-config
3. Scan I2C bus: sudo i2cdetect -y 1
4. Check sensor address (0x76 vs 0x77 for BME280)
```

**Issue: Permission Errors**
```bash
# Solution:
sudo usermod -a -G gpio,i2c,spi $USER
# Logout and login again
```

### Software Issues

**Issue: Certificate Verification Failed**
```python
# Common causes:
1. System time incorrect (check with 'date')
2. Certificate expired
3. Hostname mismatch
4. Self-signed certificate not trusted
```

**Issue: JWT Token Invalid**
```python
# Debugging steps:
1. Decode token without verification
2. Check expiration time
3. Verify secret key matches
4. Check algorithm specification
```

### Security Issues

**Issue: Students Hardcoding Secrets**
```python
# Teach proper secret management:
# BAD:
SECRET_KEY = "my-secret-key"

# GOOD:
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')
```

---

## Discussion Topics

### Week 1 Discussion: IoT Security Failures
**Case Studies:**
- Mirai Botnet (default passwords)
- Stuxnet (industrial IoT attack)
- Ring Camera vulnerabilities
- Medical device hacks

**Questions:**
- What common vulnerability patterns do you see?
- How could our security controls prevent these?
- What is the cost/benefit of security in IoT?

### Week 2 Discussion: Encryption Trade-offs
**Topics:**
- Performance impact of encryption
- Battery life considerations
- Quantum computing threats
- Encryption export regulations

### Week 3 Discussion: Authentication Challenges
**Topics:**
- Passwordless authentication
- Biometric authentication for IoT
- Zero-trust architecture
- Device identity and attestation

### Week 4 Discussion: Privacy vs. Security
**Topics:**
- Data collection ethics
- GDPR/CCPA compliance
- User consent in IoT
- Anonymization techniques

---

## Additional Resources

### Required Reading
1. "IoT Security Foundation Best Practice Guidelines"
2. OWASP IoT Top 10 (latest version)
3. NIST Cybersecurity Framework for IoT

### Recommended Books
- "Practical IoT Security" by Brian Russell
- "IoT Penetration Testing Cookbook" by Aaron Guzman
- "Hands-On IoT Security" by Sunil Cheruvu

### Online Resources
- [Raspberry Pi Security Documentation](https://www.raspberrypi.org/documentation/configuration/security.md)
- [JWT.io](https://jwt.io) - JWT debugger and documentation
- [CWE IoT Vulnerabilities](https://cwe.mitre.org/data/definitions/1425.html)

### Tools for Demonstrations
```bash
# Security Testing Tools
- Wireshark: Network traffic analysis
- OWASP ZAP: Web application security testing
- John the Ripper: Password cracking demos
- Metasploit: Vulnerability exploitation (controlled demos)
- Burp Suite: API security testing
```

### Extended Learning Opportunities
1. **Capture The Flag (CTF)**: Create IoT security CTF challenges
2. **Bug Bounty**: Participate in IoT bug bounty programs
3. **Certification Prep**: CompTIA IoT+ or CySA+
4. **Research Projects**: Contribute to IoT security research

---

## Tips for Success

### Classroom Management
1. **Pair Programming**: Have students work in pairs for complex implementations
2. **Code Reviews**: Implement peer code reviews for security
3. **Live Debugging**: Debug security issues together as a class
4. **Security Incidents**: Simulate and respond to security events

### Engagement Strategies
1. **Real-world News**: Start each class with recent IoT security news
2. **Guest Speakers**: Invite industry professionals
3. **Hands-on Demos**: Show real attacks and defenses
4. **Competition**: Create a class-wide security competition

### Assessment Best Practices
1. **Continuous Assessment**: Regular check-ins rather than single final project
2. **Peer Testing**: Students test each other's implementations
3. **Security Audits**: Formal security review process
4. **Presentation Skills**: Include security briefing presentations

### Support Resources
1. **Office Hours**: Dedicated time for security implementation help
2. **Online Forum**: Class discussion board for troubleshooting
3. **Video Tutorials**: Record common procedures
4. **Sample Code**: Provide reference implementations (with intentional vulnerabilities to fix)

---

## Contact and Support

For instructor support and resources:
- GitHub Repository: [your-github-url]
- Instructor Resources: [private-instructor-repo]
- Email Support: [your-email]
- Slack Channel: #iot-security-instructors

---

*This guide is a living document. Please contribute improvements and share your teaching experiences.*

**Version:** 1.0  
**Last Updated:** November 2024  
**Next Review:** January 2025