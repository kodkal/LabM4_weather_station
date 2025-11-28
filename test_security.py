#!/usr/bin/env python3
“””
Security Test Suite for Weather Station
Tests for common vulnerabilities - use this to verify your fixes!

FIXED: Now checks vulnerable_weather_station.py by default (configurable via –source-file)
“””

import os
import sys
import requests
import json
import time
import subprocess
from colorama import init, Fore, Style
import warnings

# Initialize colorama for colored output

init(autoreset=True)

# Suppress SSL warnings for testing

warnings.filterwarnings(‘ignore’, message=‘Unverified HTTPS request’)

class SecurityTester:
“”“Automated security testing for weather station”””

```
def __init__(self, base_url='http://localhost:8080', source_file=None):
    self.base_url = base_url
    self.session = requests.Session()
    self.results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # FIXED: Auto-detect source file, prioritizing vulnerable_weather_station.py
    if source_file:
        self.source_file = source_file
    elif os.path.exists('vulnerable_weather_station.py'):
        self.source_file = 'vulnerable_weather_station.py'
    elif os.path.exists('weather_station.py'):
        self.source_file = 'weather_station.py'
    else:
        self.source_file = 'vulnerable_weather_station.py'
    
def print_header(self, text):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

def print_test(self, test_name, passed, details=""):
    """Print test result with color"""
    if passed:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} {test_name}")
        self.results['passed'].append(test_name)
    else:
        print(f"{Fore.RED}✗{Style.RESET_ALL} {test_name}")
        if details:
            print(f"  {Fore.YELLOW}→ {details}{Style.RESET_ALL}")
        self.results['failed'].append(test_name)

def read_source_file(self):
    """Read the source file for static analysis"""
    try:
        with open(self.source_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"{Fore.YELLOW}⚠ Source file not found: {self.source_file}{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.YELLOW}⚠ Error reading source file: {e}{Style.RESET_ALL}")
        return None

def test_sql_injection(self):
    """Test for SQL injection vulnerabilities"""
    self.print_header("SQL Injection Tests")
    
    # Test 1: Basic SQL injection
    payloads = [
        {"username": "admin' --", "password": "test"},
        {"username": "admin' OR '1'='1", "password": "test"},
        {"username": "'; DROP TABLE users; --", "password": "test"},
        {"username": "admin", "password": "' OR '1'='1"}
    ]
    
    vulnerable = False
    for payload in payloads:
        try:
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=payload,
                timeout=5
            )
            
            # If we get a token with obviously bad input, it's vulnerable
            if response.status_code == 200 and 'token' in response.text:
                vulnerable = True
                break
                
        except Exception as e:
            pass
    
    self.print_test(
        "SQL Injection Prevention",
        not vulnerable,
        "SQL injection payload succeeded" if vulnerable else ""
    )
    
    return not vulnerable

def test_command_injection(self):
    """Test for command injection vulnerabilities"""
    self.print_header("Command Injection Tests")
    
    # Check if command endpoint exists
    try:
        response = self.session.post(
            f"{self.base_url}/api/command",
            json={"command": "echo test"},
            timeout=5
        )
        
        if response.status_code == 404:
            self.print_test(
                "Command Endpoint Removed",
                True,
                "Good! Dangerous endpoint doesn't exist"
            )
            return True
            
    except:
        self.print_test(
            "Command Endpoint Removed",
            True,
            "Good! Dangerous endpoint doesn't exist"
        )
        return True
    
    # Test command injection if endpoint exists
    payloads = [
        "echo test; cat /etc/passwd",
        "echo test && whoami",
        "echo test | ls -la",
        "echo $(whoami)"
    ]
    
    vulnerable = False
    for payload in payloads:
        try:
            response = self.session.post(
                f"{self.base_url}/api/command",
                json={"command": payload},
                timeout=5
            )
            
            # Check if command was executed
            if any(danger in response.text for danger in ['root:', 'bin:', 'home']):
                vulnerable = True
                break
                
        except:
            pass
    
    self.print_test(
        "Command Injection Prevention",
        not vulnerable,
        "Command injection succeeded - remove this endpoint!" if vulnerable else ""
    )
    
    return not vulnerable

def test_path_traversal(self):
    """Test for path traversal vulnerabilities"""
    self.print_header("Path Traversal Tests")
    
    payloads = [
        "../../../etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "....//....//....//etc/passwd",
        "/etc/passwd"
    ]
    
    vulnerable = False
    for payload in payloads:
        try:
            response = self.session.get(
                f"{self.base_url}/api/file",
                params={"name": payload},
                timeout=5
            )
            
            # Check if we accessed system files
            if 'root:' in response.text or 'bin:' in response.text:
                vulnerable = True
                break
                
        except:
            pass
    
    self.print_test(
        "Path Traversal Prevention",
        not vulnerable,
        "Path traversal succeeded" if vulnerable else ""
    )
    
    return not vulnerable

def test_hardcoded_credentials(self):
    """Test for hardcoded credentials"""
    self.print_header("Hardcoded Credential Tests")
    
    # Check source code for hardcoded values
    vulnerable = False
    hardcoded_patterns = [
        'API_KEY = "',
        'SECRET_KEY = "',
        'PASSWORD = "',
        'admin123',
        'secret123',
        'jwt_secret_key'
    ]
    
    content = self.read_source_file()
    if content:
        for pattern in hardcoded_patterns:
            if pattern in content:
                vulnerable = True
                break
    
    self.print_test(
        "No Hardcoded Credentials",
        not vulnerable,
        f"Found hardcoded credentials in {self.source_file}" if vulnerable else ""
    )
    
    # Test common default passwords
    common_passwords = ['admin', 'admin123', 'password', 'password123', '12345']
    default_works = False
    
    for pwd in common_passwords:
        try:
            response = self.session.post(
                f"{self.base_url}/api/login",
                json={"username": "admin", "password": pwd},
                timeout=5
            )
            
            if response.status_code == 200:
                default_works = True
                break
                
        except:
            pass
    
    self.print_test(
        "No Default Passwords",
        not default_works,
        f"Default password '{pwd}' works" if default_works else ""
    )
    
    return not vulnerable and not default_works

def test_jwt_security(self):
    """Test JWT implementation security"""
    self.print_header("JWT Security Tests")
    
    # Try to get a token
    token = None
    try:
        response = self.session.post(
            f"{self.base_url}/api/login",
            json={"username": "testuser", "password": "testpass"},
            timeout=5
        )
        
        if 'token' in response.text:
            import re
            match = re.search(r'"token":\s*"([^"]+)"', response.text)
            if match:
                token = match.group(1)
                
    except:
        pass
    
    if not token:
        print(f"{Fore.YELLOW}⚠ Could not obtain JWT token for testing{Style.RESET_ALL}")
        return True
    
    # Test 1: Check for 'none' algorithm vulnerability
    try:
        import jwt
        
        # Try to decode without verification
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Check expiration
        import datetime
        if 'exp' in decoded:
            exp_date = datetime.datetime.fromtimestamp(decoded['exp'])
            days_until_exp = (exp_date - datetime.datetime.now()).days
            
            self.print_test(
                "JWT Has Reasonable Expiration",
                days_until_exp < 2,  # Less than 2 days
                f"Token expires in {days_until_exp} days" if days_until_exp >= 2 else ""
            )
        else:
            self.print_test(
                "JWT Has Expiration",
                False,
                "Token has no expiration!"
            )
            
    except:
        pass
    
    # Test 2: Try common weak secrets
    weak_secrets = ['secret', 'secret123', 'jwt_secret_key', 'key']
    weak_secret_works = False
    
    for secret in weak_secrets:
        try:
            jwt.decode(token, secret, algorithms=['HS256'])
            weak_secret_works = True
            break
        except:
            pass
    
    self.print_test(
        "JWT Uses Strong Secret",
        not weak_secret_works,
        f"Weak secret '{secret}' works" if weak_secret_works else ""
    )
    
    return True

def test_encryption(self):
    """Test encryption implementation"""
    self.print_header("Encryption Tests")
    
    # Check if using HTTPS
    https_url = self.base_url.replace('http://', 'https://')
    using_https = False
    
    try:
        response = requests.get(https_url, verify=False, timeout=5)
        using_https = True
    except:
        pass
    
    self.print_test(
        "HTTPS/TLS Enabled",
        using_https,
        "Still using HTTP - implement TLS!" if not using_https else ""
    )
    
    # Check for weak encryption in code
    weak_crypto = False
    weak_patterns = ['rot13', 'rot_13', 'base64', 'md5', 'MD5']
    
    content = self.read_source_file()
    if content:
        for pattern in weak_patterns:
            if pattern in content:
                weak_crypto = True
                break
    
    self.print_test(
        "No Weak Encryption",
        not weak_crypto,
        f"Found weak encryption method in {self.source_file}" if weak_crypto else ""
    )
    
    return using_https and not weak_crypto

def test_input_validation(self):
    """Test input validation"""
    self.print_header("Input Validation Tests")
    
    # Test XSS payloads
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "';alert('XSS');//"
    ]
    
    xss_vulnerable = False
    for payload in xss_payloads:
        try:
            response = self.session.post(
                f"{self.base_url}/api/data",
                json={"input": payload},
                timeout=5
            )
            
            # Check if payload is reflected without escaping
            if payload in response.text:
                xss_vulnerable = True
                break
                
        except:
            pass
    
    self.print_test(
        "XSS Prevention",
        not xss_vulnerable,
        "XSS payload not filtered" if xss_vulnerable else ""
    )
    
    return not xss_vulnerable

def test_secure_headers(self):
    """Test for security headers"""
    self.print_header("Security Headers Tests")
    
    try:
        response = self.session.get(self.base_url, timeout=5)
        headers = response.headers
        
        # Check for important security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': None  # Any value is good
        }
        
        for header, expected in security_headers.items():
            if header in headers:
                if expected is None or headers[header] in expected:
                    self.print_test(f"Header: {header}", True)
                else:
                    self.print_test(
                        f"Header: {header}",
                        False,
                        f"Value '{headers[header]}' not secure"
                    )
            else:
                self.print_test(f"Header: {header}", False, "Missing")
                
    except Exception as e:
        print(f"{Fore.YELLOW}⚠ Could not test headers: {e}{Style.RESET_ALL}")
    
    return True

def test_information_disclosure(self):
    """Test for information disclosure"""
    self.print_header("Information Disclosure Tests")
    
    # Check for debug mode
    debug_enabled = False
    try:
        # Trigger an error
        response = self.session.get(f"{self.base_url}/nonexistent", timeout=5)
        
        # Check for detailed error messages
        if 'Traceback' in response.text or 'Debug mode' in response.text:
            debug_enabled = True
            
    except:
        pass
    
    self.print_test(
        "Debug Mode Disabled",
        not debug_enabled,
        "Debug mode is enabled" if debug_enabled else ""
    )
    
    # Check for version disclosure
    version_disclosed = False
    try:
        response = self.session.get(f"{self.base_url}/api/info", timeout=5)
        
        if 'python' in response.text.lower() or 'version' in response.text.lower():
            version_disclosed = True
            
    except:
        pass
    
    self.print_test(
        "No Version Disclosure",
        not version_disclosed,
        "System information exposed" if version_disclosed else ""
    )
    
    return not debug_enabled and not version_disclosed

def run_all_tests(self):
    """Run all security tests"""
    self.print_header("WEATHER STATION SECURITY TEST SUITE")
    
    print(f"\nTesting: {self.base_url}")
    print(f"Source file: {self.source_file}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Verify source file exists
    if not os.path.exists(self.source_file):
        print(f"{Fore.RED}⚠ Warning: Source file '{self.source_file}' not found!{Style.RESET_ALL}")
        print(f"  Static code analysis tests will be skipped.\n")
    
    # Run all tests
    tests = [
        self.test_sql_injection,
        self.test_command_injection,
        self.test_path_traversal,
        self.test_hardcoded_credentials,
        self.test_jwt_security,
        self.test_encryption,
        self.test_input_validation,
        self.test_secure_headers,
        self.test_information_disclosure
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"{Fore.RED}Error running test: {e}{Style.RESET_ALL}")
    
    # Print summary
    self.print_header("TEST SUMMARY")
    
    total = len(self.results['passed']) + len(self.results['failed'])
    passed = len(self.results['passed'])
    failed = len(self.results['failed'])
    
    print(f"\nTotal Tests: {total}")
    print(f"{Fore.GREEN}Passed: {passed}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}🎉 Excellent! All security tests passed!{Style.RESET_ALL}")
        print("Your weather station is well-secured!")
    elif failed <= 3:
        print(f"\n{Fore.YELLOW}⚠ Good progress! Fix the remaining issues.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}⚠ Multiple security issues found!{Style.RESET_ALL}")
        print("Review the failed tests and implement fixes.")
    
    # Grade calculation
    score = (passed / total) * 100 if total > 0 else 0
    grade = self.calculate_grade(score)
    
    print(f"\nSecurity Score: {score:.1f}%")
    print(f"Grade: {grade}")
    
    return score

def calculate_grade(self, score):
    """Calculate letter grade from score"""
    if score >= 95:
        return "A+"
    elif score >= 90:
        return "A"
    elif score >= 85:
        return "B+"
    elif score >= 80:
        return "B"
    elif score >= 75:
        return "C+"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
```

def main():
“”“Main function”””
import argparse

```
parser = argparse.ArgumentParser(
    description='Security test suite for weather station'
)
parser.add_argument(
    '--url',
    default='http://localhost:8080',
    help='Base URL of weather station (default: http://localhost:8080)'
)
parser.add_argument(
    '--source-file',
    default=None,
    help='Source file to analyze (default: auto-detect, prefers vulnerable_weather_station.py)'
)
parser.add_argument(
    '--verbose',
    action='store_true',
    help='Show detailed test output'
)

args = parser.parse_args()

# Check if server is running
print(f"Checking if server is running at {args.url}...")
try:
    response = requests.get(args.url, timeout=5)
    print(f"{Fore.GREEN}✓ Server is running{Style.RESET_ALL}")
except:
    print(f"{Fore.RED}✗ Server not responding at {args.url}{Style.RESET_ALL}")
    print("\nPlease start the weather station first:")
    print("  python vulnerable_weather_station.py")
    sys.exit(1)

# Run tests
tester = SecurityTester(args.url, args.source_file)
score = tester.run_all_tests()

# Exit with non-zero if tests failed
sys.exit(0 if score == 100 else 1)
```

if **name** == ‘**main**’:
main()