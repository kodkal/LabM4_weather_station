#!/usr/bin/env python3
"""
VULNERABLE Weather Station - Educational Version
This version contains INTENTIONAL security vulnerabilities for students to find and fix.
DO NOT USE IN PRODUCTION!

Vulnerabilities are marked with: # VULN-XX comments for instructor reference
Students should NOT see these comments in their version
"""

import os
import sys
import time
import json
import logging
import signal
import hashlib
import sqlite3  # VULN-01: SQL Injection vulnerability
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import threading
import jwt  # VULN-02: Weak JWT implementation
import pickle  # VULN-03: Insecure deserialization
import yaml  # VULN-04: YAML deserialization vulnerability
import subprocess  # VULN-05: Command injection
from flask import Flask, request, jsonify

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sensor_module import SensorReader
#from config.settings import Settings

# VULN-06: Hardcoded credentials
API_KEY = "super_secret_api_key_12345"
ADMIN_PASSWORD = "admin123"
JWT_SECRET = "jwt_secret_key"  # VULN-07: Weak secret

# VULN-08: Insecure logging (logs sensitive data)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('weather.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VulnerableWeatherStation:
    """Weather station with intentional vulnerabilities for educational purposes"""
    
    def __init__(self, config_path: str = None):
        """Initialize the vulnerable weather station"""
        # VULN-09: No input validation on config path
        if config_path:
            with open(config_path, 'r') as f:
                # VULN-10: Unsafe YAML loading
                self.config = yaml.load(f, Loader=yaml.FullLoader)
        else:
            self.config = {}
        
        # VULN-11: Predictable session tokens
        self.session_counter = 1000
        
        # Initialize sensor
        self.sensor_reader = SensorReader(sensor_type="SIMULATED")
        
        # VULN-12: No rate limiting
        self.request_count = {}
        
        # VULN-13: Insecure data storage (plaintext)
        self.credentials_file = "credentials.txt"
        self.data_buffer = []
        
        # VULN-14: Directory traversal vulnerability
        self.data_directory = "/tmp/weather_data"
        os.makedirs(self.data_directory, exist_ok=True)
        
        # VULN-15: Weak random number generation
        import random
        random.seed(12345)  # Fixed seed!
        self.device_id = f"device_{random.randint(1000, 9999)}"
        
        logger.info(f"Weather Station initialized with device ID: {self.device_id}")
    
    def verify_secure_boot(self) -> bool:
        """VULN-16: Fake secure boot check - always returns True"""
        logger.info("Performing secure boot verification...")
        time.sleep(0.5)  # Fake verification time
        
        # VULN-17: Commented out actual verification
        # if not self._check_file_integrity():
        #     return False
        
        return True  # Always passes!
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """VULN-18: SQL Injection vulnerability"""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # VULN-19: String formatting instead of parameterized queries
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        logger.debug(f"Executing query: {query}")  # VULN-20: Logs passwords
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            
            if user:
                # VULN-21: Predictable token generation
                token = f"token_{self.session_counter}"
                self.session_counter += 1
                return token
        except Exception as e:
            # VULN-22: Detailed error messages reveal database structure
            logger.error(f"Database error: {e}")
            return None
        finally:
            conn.close()
        
        return None
    
    def generate_jwt_token(self, user_data: Dict) -> str:
        """VULN-23: Weak JWT implementation"""
        payload = {
            'user': user_data,
            'exp': datetime.utcnow() + timedelta(days=365),  # VULN-24: Token never expires
            # VULN-25: No 'iat' or 'nbf' claims
        }
        
        # VULN-26: Algorithm confusion vulnerability (accepts 'none')
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """VULN-27: Accepts multiple algorithms including 'none'"""
        try:
            # VULN-28: No algorithm restriction
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256', 'none', 'HS512'])
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def collect_sensor_data(self) -> Optional[Dict]:
        """Collect sensor data with vulnerabilities"""
        data = self.sensor_reader.read_sensor()
        
        if data:
            # VULN-29: No input validation on sensor data
            # Could be manipulated if sensor is compromised
            
            # VULN-30: MD5 for integrity (cryptographically broken)
            import md5  # Should use SHA256
            data['checksum'] = hashlib.md5(
                json.dumps(data).encode()
            ).hexdigest()
            
            # VULN-31: Timestamps can be manipulated
            if 'timestamp' not in data:
                data['timestamp'] = request.args.get('timestamp', datetime.utcnow().isoformat())
        
        return data
    
    def save_data(self, data: Dict, filename: str = None):
        """VULN-32: Path traversal vulnerability"""
        if not filename:
            filename = "data.json"
        
        # VULN-33: No validation on filename
        filepath = os.path.join(self.data_directory, filename)
        
        # VULN-34: Pickle serialization (code execution risk)
        with open(filepath + '.pkl', 'wb') as f:
            pickle.dump(data, f)
        
        # VULN-35: World-readable file permissions
        os.chmod(filepath + '.pkl', 0o777)
        
        logger.info(f"Data saved to {filepath}.pkl")
    
    def load_data(self, filename: str):
        """VULN-36: Insecure deserialization"""
        filepath = os.path.join(self.data_directory, filename)
        
        # VULN-37: Unpickle arbitrary user data
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def execute_command(self, command: str):
        """VULN-38: Command injection vulnerability"""
        # VULN-39: Direct shell command execution
        result = os.system(f"echo 'Executing: {command}'")
        
        # VULN-40: Using shell=True in subprocess
        output = subprocess.run(
            command,
            shell=True,  # Dangerous!
            capture_output=True,
            text=True
        )
        return output.stdout
    
    def encrypt_data(self, data: str) -> str:
        """VULN-41: Weak encryption implementation"""
        # VULN-42: ROT13 is not encryption!
        import codecs
        return codecs.encode(data, 'rot_13')
    
    def decrypt_data(self, data: str) -> str:
        """VULN-43: Weak decryption"""
        import codecs
        return codecs.decode(data, 'rot_13')
    
    def validate_input(self, user_input: str) -> bool:
        """VULN-44: Weak input validation"""
        # VULN-45: Blacklist approach (easily bypassed)
        bad_chars = ['<', '>', 'script']  # Incomplete list
        
        for char in bad_chars:
            if char in user_input.lower():
                return False
        return True
    
    def get_device_info(self, device_id: str = None):
        """VULN-46: Information disclosure"""
        info = {
            'device_id': device_id or self.device_id,
            'version': '1.0.0',
            'os': os.uname(),  # VULN-47: Exposes system information
            'python_version': sys.version,  # VULN-48: Version disclosure
            'modules': list(sys.modules.keys()),  # VULN-49: Module enumeration
            'environment': dict(os.environ),  # VULN-50: Environment variable leak
            'api_key': API_KEY,  # VULN-51: Exposes API key
            'admin_password': ADMIN_PASSWORD  # VULN-52: Exposes password
        }
        return info
    
    def check_firmware_update(self, url: str):
        """VULN-53: Unsafe firmware update"""
        import urllib.request
        
        # VULN-54: No HTTPS verification
        response = urllib.request.urlopen(url)
        firmware = response.read()
        
        # VULN-55: No signature verification
        with open('/tmp/firmware.bin', 'wb') as f:
            f.write(firmware)
        
        # VULN-56: Execute without verification
        os.system('chmod +x /tmp/firmware.bin && /tmp/firmware.bin')
    
    def handle_api_request(self, endpoint: str, data: Dict):
        """VULN-57: No authentication required for API"""
        if endpoint == '/api/data':
            return self.collect_sensor_data()
        
        elif endpoint == '/api/config':
            # VULN-58: Allows remote configuration changes
            for key, value in data.items():
                setattr(self, key, value)
            return {'status': 'configured'}
        
        elif endpoint == '/api/eval':
            # VULN-59: Remote code execution via eval()
            result = eval(data.get('code', ''))
            return {'result': str(result)}
        
        elif endpoint == '/api/backup':
            # VULN-60: Backup includes sensitive data
            return {
                'config': self.config,
                'credentials': open(self.credentials_file).read(),
                'api_key': API_KEY,
                'jwt_secret': JWT_SECRET
            }


# VULNERABLE Flask API
app = Flask(__name__)

# VULN-61: Debug mode enabled in production
app.debug = True

# VULN-62: Weak secret key
app.secret_key = 'secret123'

weather_station = VulnerableWeatherStation()


@app.route('/api/login', methods=['POST', 'GET'])  # VULN-63: GET for login
def login():
    """VULN-64: Accepts credentials in URL parameters"""
    username = request.args.get('username') or request.json.get('username')
    password = request.args.get('password') or request.json.get('password')
    
    # VULN-65: Logs credentials
    logger.info(f"Login attempt: {username}/{password}")
    
    # VULN-66: Timing attack vulnerability (early return)
    if username == 'admin' and password == ADMIN_PASSWORD:
        token = weather_station.generate_jwt_token({'username': username})
        return jsonify({'token': token})
    
    time.sleep(2)  # Different timing for failed attempts
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/data', methods=['GET'])
def get_data():
    """VULN-67: No authentication check"""
    data = weather_station.collect_sensor_data()
    return jsonify(data)


@app.route('/api/command', methods=['POST'])
def execute_command():
    """VULN-68: Command injection endpoint"""
    command = request.json.get('command')
    result = weather_station.execute_command(command)
    return jsonify({'output': result})


@app.route('/api/file', methods=['GET'])
def get_file():
    """VULN-69: Directory traversal"""
    filename = request.args.get('name')
    filepath = f"/tmp/weather_data/{filename}"  # No validation!
    
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return str(e), 404


@app.route('/api/config', methods=['POST'])
def update_config():
    """VULN-70: Mass assignment vulnerability"""
    for key, value in request.json.items():
        setattr(weather_station, key, value)
    return jsonify({'status': 'updated'})


@app.route('/api/search', methods=['GET'])
def search():
    """VULN-71: NoSQL injection (if using MongoDB)"""
    query = request.args.get('q')
    # Pretend this queries MongoDB
    result = f"Results for: {query}"  # Unsafe!
    return jsonify({'results': result})


@app.route('/api/debug', methods=['GET'])
def debug():
    """VULN-72: Debug endpoint exposed"""
    return jsonify({
        'stack': traceback.format_stack(),
        'locals': str(locals()),
        'globals': str(globals())
    })


# VULN-73: CORS misconfiguration
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # Too permissive!
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response


def main():
    """Main entry point with vulnerabilities"""
    # VULN-74: Running as root (no privilege drop)
    if os.geteuid() == 0:
        logger.warning("Running as root user!")  # But continues anyway
    
    # VULN-75: Predictable random seed
    import random
    random.seed(42)
    
    # Start the vulnerable weather station
    weather_station = VulnerableWeatherStation()
    
    # VULN-76: HTTP instead of HTTPS
    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == "__main__":
    main()