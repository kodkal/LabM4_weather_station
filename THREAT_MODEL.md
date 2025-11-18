# Threat Model Document
## Weather Station IoT Security - Threat Analysis

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
[Explain the purpose of this threat model in 2-3 sentences]

### 1.2 Methodology
Threat modeling approach used:
- [ ] STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege)
- [ ] DREAD (Damage, Reproducibility, Exploitability, Affected Users, Discoverability)
- [ ] PASTA (Process for Attack Simulation and Threat Analysis)
- [ ] Other: [Specify]

### 1.3 Risk Rating Scale
| Rating | Score | Description |
|--------|-------|-------------|
| Critical | 9-10 | Immediate action required |
| High | 7-8 | Address within this lab |
| Medium | 5-6 | Should be addressed |
| Low | 3-4 | Monitor and track |
| Info | 1-2 | Acceptable risk |

---

## 2. System Overview

### 2.1 System Boundaries
```
┌─────────────────────────────────────────────┐
│          TRUST BOUNDARY                      │
│                                              │
│  ┌──────────┐      ┌──────────────┐        │
│  │ Sensors  │─────▶│ Weather       │        │
│  └──────────┘      │ Station App   │        │
│                    └──────┬─────────┘        │
│                           │                  │
│                    ┌──────▼─────────┐        │
│                    │   Database     │        │
│                    └────────────────┘        │
│                           │                  │
└───────────────────────────┼──────────────────┘
                            │
                    ┌───────▼────────┐
                    │ External Users  │
                    └────────────────┘
```

### 2.2 Assets to Protect

| Asset | Type | Value | Description |
|-------|------|-------|-------------|
| Sensor Data | Data | High | Temperature, humidity, pressure readings |
| API Keys | Credential | Critical | Authentication tokens |
| User Credentials | Credential | Critical | Usernames and passwords |
| System Configuration | Config | High | System settings and parameters |
| Historical Data | Data | Medium | Stored sensor readings |
| System Availability | Service | High | Uptime and accessibility |
| [Add more] | | | |

### 2.3 Trust Boundaries
1. **Physical Boundary**: Raspberry Pi hardware
2. **Network Boundary**: Local network vs Internet
3. **Process Boundary**: Application vs Operating System
4. **User Boundary**: Authenticated vs Anonymous users

---

## 3. Threat Actors

### 3.1 Potential Attackers

| Actor | Motivation | Capability | Access | Threat Level |
|-------|------------|------------|---------|--------------|
| Script Kiddie | Curiosity, Fame | Low | Remote | Low |
| Competitor | Business advantage | Medium | Remote | Medium |
| Insider | Revenge, Profit | High | Physical | High |
| Hacktivist | Ideology | Medium | Remote | Medium |
| Nation State | Espionage | Very High | Remote | Critical |
| Malware/Bot | Crypto mining, DDoS | Medium | Remote | Medium |
| [Add more] | | | | |

### 3.2 Attack Vectors
- [ ] Network attacks (Remote)
- [ ] Physical access to device
- [ ] Supply chain compromise
- [ ] Social engineering
- [ ] Insider threat
- [ ] Malware infection
- [ ] Other: [Specify]

---

## 4. STRIDE Threat Analysis

### 4.1 Spoofing Identity

| Threat ID | Description | Component | Likelihood | Impact | Risk | Mitigation |
|-----------|-------------|-----------|------------|---------|------|------------|
| S-01 | Attacker spoofs device identity | API | High | High | 8 | Implement device certificates |
| S-02 | User impersonation | Login | Medium | High | 6 | Strong authentication |
| S-03 | [Add more] | | | | | |

### 4.2 Tampering with Data

| Threat ID | Description | Component | Likelihood | Impact | Risk | Mitigation |
|-----------|-------------|-----------|------------|---------|------|------------|
| T-01 | Modify sensor readings | Sensor Module | Medium | High | 6 | Data integrity checks |
| T-02 | Alter configuration files | File System | Low | Critical | 6 | File integrity monitoring |
| T-03 | SQL injection to modify data | Database | High | Critical | 9 | Parameterized queries |
| T-04 | [Add more] | | | | | |

### 4.3 Repudiation

| Threat ID | Description | Component | Likelihood | Impact | Risk | Mitigation |
|-----------|-------------|-----------|------------|---------|------|------------|
| R-01 | User denies actions | API | Medium | Medium | 4 | Comprehensive logging |
| R-02 | No audit trail | System | High | Medium | 6 | Implement audit logs |
| R-03 | [Add more] | | | | | |

### 4.4 Information Disclosure

| Threat ID | Description | Component | Likelihood | Impact | Risk | Mitigation |
|-----------|-------------|-----------|------------|---------|------|------------|
| I-01 | Hardcoded credentials exposed | Source Code | Critical | Critical | 10 | Use environment variables |
| I-02 | Unencrypted data transmission | Network | High | High | 8 | Implement TLS |
| I-03 | Debug info in production | Logs | High | Medium | 6 | Disable debug mode |
| I-04 | [Add more] | | | | | |

### 4.5 Denial of Service

| Threat ID | Description | Component | Likelihood | Impact | Risk | Mitigation |
|-----------|-------------|-----------|------------|---------|------|------------|
| D-01 | API request flooding | API | High | High | 8 | Rate limiting |
| D-02 | Resource exhaustion | System | Medium | High | 6 | Resource monitoring |
| D-03 | [Add more] | | | | | |

### 4.6 Elevation of Privilege

| Threat ID | Description | Component | Likelihood | Impact | Risk | Mitigation |
|-----------|-------------|-----------|------------|---------|------|------------|
| E-01 | Command injection for root | System | Medium | Critical | 8 | Input validation |
| E-02 | Privilege escalation via API | API | Low | High | 5 | Proper authorization |
| E-03 | [Add more] | | | | | |

---

## 5. Attack Trees

### 5.1 Compromise Weather Station Data
```
Goal: Compromise Weather Station
├── OR Physical Access
│   ├── Steal Raspberry Pi
│   ├── Access during maintenance
│   └── Social engineering
├── OR Remote Access
│   ├── AND Network Attack
│   │   ├── Find exposed service
│   │   ├── Exploit vulnerability
│   │   └── Gain shell access
│   ├── AND Web Application Attack
│   │   ├── SQL injection
│   │   ├── Command injection
│   │   └── Authentication bypass
│   └── AND API Attack
│       ├── Stolen credentials
│       ├── Token manipulation
│       └── Replay attack
└── OR Supply Chain
    ├── Compromised dependencies
    └── Malicious updates
```

### 5.2 Data Manipulation Attack
```
Goal: Manipulate Sensor Data
├── OR Direct Manipulation
│   ├── Compromise sensor hardware
│   ├── Man-in-the-middle attack
│   └── Database manipulation
└── OR Indirect Manipulation
    ├── API parameter tampering
    ├── Configuration file modification
    └── Cache poisoning
```

---

## 6. Vulnerability Assessment

### 6.1 Technical Vulnerabilities Found

| CVE/ID | Vulnerability | CVSS Score | Component | Status | Fix Applied |
|--------|--------------|------------|-----------|---------|-------------|
| CUSTOM-01 | SQL Injection | 9.8 | Login API | Fixed ✓ | Parameterized queries |
| CUSTOM-02 | Hardcoded Secrets | 7.5 | Config | Fixed ✓ | Environment variables |
| CUSTOM-03 | No Input Validation | 8.1 | Multiple | Fixed ✓ | Input sanitization |
| CUSTOM-04 | Weak Encryption | 6.5 | Data Store | Fixed ✓ | AES-256 |
| CUSTOM-05 | Missing Auth | 9.1 | API | Fixed ✓ | JWT implementation |
| [Add more] | | | | | |

### 6.2 Configuration Vulnerabilities

| Issue | Description | Risk | Mitigation Status |
|-------|-------------|------|-------------------|
| Default Passwords | System uses default credentials | High | Changed ✓ |
| Open Ports | Unnecessary services exposed | Medium | Disabled ✓ |
| Debug Mode | Debug enabled in production | Medium | Disabled ✓ |
| [Add more] | | | |

---

## 7. Risk Matrix

### 7.1 Risk Visualization

```
Impact ↑
       │
  High │ [T-02] [S-01] [I-01]
       │        [D-01] [E-01]
       │
Medium │ [R-01] [I-03] [T-01]
       │ [R-02]
       │
   Low │ [Other threats...]
       │
       └────────────────────────► Likelihood
          Low    Medium   High
```

### 7.2 Risk Priority

| Priority | Threat IDs | Action Required |
|----------|------------|-----------------|
| 1 (Critical) | I-01, T-03 | Immediate fix |
| 2 (High) | S-01, I-02, D-01, E-01 | Fix in this lab |
| 3 (Medium) | T-01, R-02, I-03 | Should address |
| 4 (Low) | R-01, T-02 | Monitor |

---

## 8. Mitigation Strategies

### 8.1 Implemented Mitigations

| Threat | Mitigation | Implementation | Effectiveness |
|--------|------------|----------------|---------------|
| SQL Injection | Parameterized queries | `cursor.execute(query, params)` | High |
| Hardcoded Creds | Environment variables | `.env` file with `python-dotenv` | High |
| Weak Encryption | AES-256 | `cryptography` library | High |
| No Auth | JWT tokens | `PyJWT` with expiration | High |
| [Add actual mitigations] | | | |

### 8.2 Recommended Additional Mitigations

| Priority | Mitigation | Effort | Impact | Notes |
|----------|------------|--------|---------|--------|
| High | Implement HTTPS | Medium | High | Protect data in transit |
| High | Add rate limiting | Low | High | Prevent DoS |
| Medium | Enable audit logging | Low | Medium | Track security events |
| Medium | Implement RBAC | High | Medium | Role-based access |
| Low | Add CAPTCHA | Medium | Low | Prevent automation |
| [Add more] | | | | |

---

## 9. Security Controls Mapping

### 9.1 Preventive Controls
- [x] Input validation
- [x] Authentication mechanism
- [x] Encryption at rest
- [x] Encryption in transit
- [ ] Access control lists
- [ ] Network segmentation
- [ ] Other: [Specify]

### 9.2 Detective Controls
- [x] Logging and monitoring
- [x] Integrity checking
- [ ] Intrusion detection
- [ ] Anomaly detection
- [ ] Other: [Specify]

### 9.3 Corrective Controls
- [x] Error handling
- [x] Backup and recovery
- [ ] Incident response plan
- [ ] Automated rollback
- [ ] Other: [Specify]

---

## 10. Residual Risk

### 10.1 Accepted Risks

| Risk | Justification | Compensating Controls |
|------|---------------|----------------------|
| Self-signed certificates | Educational environment | Would use CA in production |
| No hardware security module | Cost constraints | Software-based key storage |
| Limited monitoring | Resource constraints | Basic logging implemented |
| [Add more] | | |

### 10.2 Risk Treatment Summary

| Total Threats | Mitigated | Accepted | Transferred | Avoided |
|---------------|-----------|----------|-------------|---------|
| [Number] | [Number] | [Number] | 0 | 0 |

---

## 11. Testing & Validation

### 11.1 Security Testing Performed

| Test Type | Tool Used | Results | Evidence |
|-----------|-----------|---------|----------|
| Vulnerability Scan | `test_security.py` | [Score]% | Screenshot #19 |
| SQL Injection Test | Manual + sqlmap | Blocked | Screenshot #20 |
| Authentication Test | Curl commands | Working | Test logs |
| Encryption Verification | Wireshark | Encrypted | Packet capture |
| [Add more] | | | |

### 11.2 Penetration Testing Scenarios

| Scenario | Method | Result | Fix Applied |
|----------|--------|--------|-------------|
| Bypass authentication | Token manipulation | Failed ✓ | Proper validation |
| Extract credentials | Code review | Failed ✓ | Removed hardcoding |
| Inject malicious data | Various payloads | Failed ✓ | Input validation |
| [Add more] | | | |

---

## 12. Compliance Mapping

### 12.1 OWASP IoT Top 10 Coverage

| # | Vulnerability | Addressed | How |
|---|--------------|-----------|-----|
| I1 | Weak Passwords | ✓ | Strong password policy |
| I2 | Insecure Network Services | ✓ | Disabled unnecessary services |
| I3 | Insecure Ecosystem | ✓ | Secure API design |
| I4 | Lack of Secure Update | Partial | Basic verification |
| I5 | Insecure Components | ✓ | Updated dependencies |
| I6 | Insufficient Privacy | ✓ | Data encryption |
| I7 | Insecure Data Transfer | ✓ | TLS implementation |
| I8 | Lack of Device Management | Partial | Basic monitoring |
| I9 | Insecure Default Settings | ✓ | Secure defaults |
| I10 | Lack of Physical Hardening | N/A | Educational environment |

---

## 13. Recommendations

### 13.1 Immediate Actions
1. [Action 1 with justification]
2. [Action 2 with justification]
3. [Action 3 with justification]

### 13.2 Short-term Improvements (1-3 months)
1. [Improvement 1]
2. [Improvement 2]
3. [Improvement 3]

### 13.3 Long-term Strategy (3-12 months)
1. [Strategy 1]
2. [Strategy 2]
3. [Strategy 3]

---

## 14. Conclusion

### 14.1 Overall Risk Assessment
Current security posture: [Low/Medium/High]
- **Before mitigations**: [Score/10]
- **After mitigations**: [Score/10]
- **Improvement**: [Percentage]%

### 14.2 Key Achievements
1. [Achievement 1]
2. [Achievement 2]
3. [Achievement 3]

### 14.3 Lessons Learned
1. [Lesson 1]
2. [Lesson 2]
3. [Lesson 3]

---

## Appendices

### Appendix A: Threat Modeling Tools Used
- [ ] Microsoft Threat Modeling Tool
- [ ] OWASP Threat Dragon
- [x] Manual analysis
- [ ] Other: [Specify]

### Appendix B: References
1. STRIDE Threat Model: https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
2. OWASP IoT Security: https://owasp.org/www-project-internet-of-things/
3. NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
4. [Add more references]

### Appendix C: Acronyms
- **API**: Application Programming Interface
- **CVE**: Common Vulnerabilities and Exposures
- **CVSS**: Common Vulnerability Scoring System
- **DoS**: Denial of Service
- **IoT**: Internet of Things
- **RBAC**: Role-Based Access Control
- **TLS**: Transport Layer Security
- [Add more as needed]

---

## Approval

**Student Signature**: _______________________  
**Date**: _______________________

**Instructor Review**: _______________________  
**Grade**: _______________________

---

*Threat Model Document v1.0 | Module 4 - IoT Security | UVU*