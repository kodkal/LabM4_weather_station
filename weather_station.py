#!/usr/bin/env python3
"""
Secure Weather Station - Main Application
IoT Security Project for UVU
"""

import os
import sys
import time
import json
import logging
import signal
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth import JWTManager
from encryption import SecureDataTransmission
from validation import InputValidator
from credentials import SecureCredentialStore
from sensor_module import SensorReader
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


# from api.server import create_api_server  # Comment out or remove
import settings

class SecureWeatherStation:
    """Main weather station application with security controls"""
    
    def __init__(self, config_path: str = None):
        """Initialize the secure weather station"""
        # Load configuration
        self.settings = settings
        
        # Setup secure logging
        self._setup_logging()
        
        # Initialize security components
        self._initialize_security()
        
        # Initialize sensor
        # If simulation, don't pass gpio_pin
        if self.settings.SENSOR_SIMULATION or self.settings.SENSOR_TYPE == 'SIMULATED':
            self.sensor_reader = SensorReader(sensor_type='SIMULATED')
        else:
            self.sensor_reader = SensorReader(
            sensor_type=self.settings.SENSOR_TYPE,
            gpio_pin=self.settings.SENSOR_PIN
        )

        
        # Initialize data storage
        self.data_buffer: List[Dict] = []
        self.max_buffer_size = 100
        
        # Threading controls
        self.running = False
        self.data_thread = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Secure Weather Station initialized", 
                        extra={"event": "startup", "version": "1.0.0"})
    
    def _setup_logging(self):
        """Configure secure logging with JSON format"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Setup JSON logging for security events
        logHandler = RotatingFileHandler(
            'logs/weather_station.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)
        
        self.logger = logging.getLogger('SecureWeatherStation')
        self.logger.addHandler(logHandler)
        self.logger.setLevel(logging.INFO)
        
        # Also log to console in development
        if self.settings.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(console_handler)
    
    def _initialize_security(self):
        """Initialize all security components"""
        # Secure credential storage
        self.credential_store = SecureCredentialStore(
            key_file=self.settings.KEY_FILE
        )
        
        # JWT authentication manager
        self.jwt_manager = JWTManager(
            secret_key=self.credential_store.get_or_create_secret('jwt_secret'),
            algorithm='HS256',
            token_expiry=timedelta(hours=24)
        )
        
        # Secure data transmission
        self.secure_transmission = SecureDataTransmission(
            cert_file=self.settings.CERT_FILE,
            key_file=self.settings.PRIVATE_KEY_FILE
        )
        
        # Input validator
        self.input_validator = InputValidator()
        
        self.logger.info("Security components initialized",
                        extra={"event": "security_init"})
    
    def verify_secure_boot(self) -> bool:
        """Verify secure boot configuration"""
        try:
            # Check if secure boot is enabled (simplified for educational purposes)
            # In production, this would verify actual UEFI secure boot status
            
            # Check for boot partition integrity
            boot_hash = self._calculate_boot_hash()
            stored_hash = self.credential_store.get_credential('boot_hash')
            
            if stored_hash is None:
                # First boot, store the hash
                self.credential_store.store_credential('boot_hash', boot_hash)
                self.logger.info("Boot hash stored for future verification")
                return True
            
            if boot_hash != stored_hash:
                self.logger.error("Boot integrity check failed!",
                                extra={"event": "boot_verification_failed"})
                return False
            
            # Check for required security configurations
            security_checks = {
                'ssh_keys': self._check_ssh_configuration(),
                'firewall': self._check_firewall_status(),
                'file_permissions': self._check_file_permissions(),
                'kernel_modules': self._check_kernel_modules()
            }
            
            for check, status in security_checks.items():
                if not status:
                    self.logger.warning(f"Security check failed: {check}",
                                      extra={"event": "security_check_failed", 
                                           "check": check})
            
            all_passed = all(security_checks.values())
            
            self.logger.info("Secure boot verification completed",
                           extra={"event": "boot_verification", 
                                "status": "passed" if all_passed else "failed",
                                "checks": security_checks})
            
            return all_passed
            
        except Exception as e:
            self.logger.error(f"Error during secure boot verification: {e}",
                            extra={"event": "boot_verification_error"})
            return False
    
    def _calculate_boot_hash(self) -> str:
        """Calculate hash of critical boot files"""
        hasher = hashlib.sha256()
        critical_files = [
            '/boot/config.txt',
            '/boot/cmdline.txt',
            sys.executable  # Python interpreter
        ]
        
        for filepath in critical_files:
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'rb') as f:
                        hasher.update(f.read())
                except Exception as e:
                    self.logger.warning(f"Could not hash {filepath}: {e}")
        
        return hasher.hexdigest()
    
    def _check_ssh_configuration(self) -> bool:
        """Check SSH security configuration"""
        try:
            ssh_config_path = '/etc/ssh/sshd_config'
            if not os.path.exists(ssh_config_path):
                return True  # SSH might not be installed
            
            with open(ssh_config_path, 'r') as f:
                config = f.read()
            
            # Check for secure configurations
            secure_settings = [
                'PermitRootLogin no' in config or 'PermitRootLogin prohibit-password' in config,
                'PasswordAuthentication no' in config or 'PasswordAuthentication' not in config,
                'PubkeyAuthentication yes' in config or 'PubkeyAuthentication' not in config
            ]
            
            return all(secure_settings)
        except Exception:
            return False
    
    def _check_firewall_status(self) -> bool:
        """Check if firewall is configured"""
        # Simplified check - in production, verify iptables or ufw rules
        return os.path.exists('/etc/iptables/rules.v4') or os.path.exists('/etc/ufw/ufw.conf')
    
    def _check_file_permissions(self) -> bool:
        """Check critical file permissions"""
        try:
            # Check that our key files have appropriate permissions
            if os.path.exists(self.settings.KEY_FILE):
                stat_info = os.stat(self.settings.KEY_FILE)
                # Check that only owner can read/write (0600)
                return (stat_info.st_mode & 0o777) == 0o600
            return True
        except Exception:
            return False
    
    def _check_kernel_modules(self) -> bool:
        """Check for suspicious kernel modules"""
        try:
            # In production, check for known malicious modules
            with open('/proc/modules', 'r') as f:
                modules = f.read()
            
            # List of suspicious module patterns (simplified)
            suspicious = ['rootkit', 'backdoor', 'keylogger']
            
            for pattern in suspicious:
                if pattern in modules.lower():
                    return False
            
            return True
        except Exception:
            return True  # Assume safe if we can't check
    
    def collect_sensor_data(self) -> Optional[Dict]:
        """Collect and validate sensor data"""
        try:
            # Read sensor data
            raw_data = self.sensor_reader.read_sensor()
            
            if raw_data is None:
                self.logger.warning("No data from sensor")
                return None
            
            # Validate sensor data
            if not self.input_validator.validate_sensor_data(raw_data):
                self.logger.warning("Invalid sensor data detected",
                                  extra={"event": "invalid_sensor_data", 
                                       "data": raw_data})
                return None
            
            # Add metadata
            sensor_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'device_id': self.settings.DEVICE_ID,
                'location': self.settings.LOCATION,
                'temperature': raw_data.get('temperature'),
                'humidity': raw_data.get('humidity'),
                'pressure': raw_data.get('pressure'),
                'data_integrity': self._calculate_data_hash(raw_data)
            }
            
            self.logger.debug("Sensor data collected",
                            extra={"event": "data_collection", 
                                 "temperature": sensor_data['temperature']})
            
            return sensor_data
            
        except Exception as e:
            self.logger.error(f"Error collecting sensor data: {e}",
                            extra={"event": "sensor_error"})
            return None
    
    def _calculate_data_hash(self, data: Dict) -> str:
        """Calculate integrity hash for sensor data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def transmit_data(self, data: Dict) -> bool:
        """Securely transmit data to server"""
        try:
            # Encrypt data
            encrypted_data = self.secure_transmission.encrypt_data(data)
            
            # Generate auth token
            token = self.jwt_manager.generate_token({
                'device_id': self.settings.DEVICE_ID,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Prepare transmission
            payload = {
                'data': encrypted_data,
                'signature': self.secure_transmission.sign_data(encrypted_data)
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Send data (simulated for now)
            self.logger.info("Data transmitted securely",
                           extra={"event": "data_transmission",
                                "size": len(encrypted_data)})
            
            # Add to buffer for API access
            self.data_buffer.append(data)
            if len(self.data_buffer) > self.max_buffer_size:
                self.data_buffer.pop(0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error transmitting data: {e}",
                            extra={"event": "transmission_error"})
            return False
    
    def data_collection_loop(self):
        """Main loop for continuous data collection"""
        self.logger.info("Starting data collection loop")
        
        while self.running:
            try:
                # Collect sensor data
                data = self.collect_sensor_data()
                
                if data:
                    # Transmit data securely
                    success = self.transmit_data(data)
                    
                    if not success:
                        # Store locally if transmission fails
                        self._store_local_backup(data)
                
                # Wait for next reading
                time.sleep(self.settings.READING_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Error in data collection loop: {e}",
                                extra={"event": "loop_error"})
                time.sleep(5)  # Brief pause before retry
    
    def _store_local_backup(self, data: Dict):
        """Store data locally if transmission fails"""
        try:
            backup_dir = 'data_backup'
            os.makedirs(backup_dir, exist_ok=True)
            
            filename = f"{backup_dir}/backup_{datetime.utcnow().timestamp()}.json"
            
            # Encrypt before storing
            encrypted = self.secure_transmission.encrypt_data(data)
            
            with open(filename, 'w') as f:
                json.dump({
                    'encrypted_data': encrypted,
                    'timestamp': datetime.utcnow().isoformat()
                }, f)
            
            self.logger.info("Data backed up locally",
                           extra={"event": "local_backup", "file": filename})
            
        except Exception as e:
            self.logger.error(f"Failed to store local backup: {e}",
                            extra={"event": "backup_error"})
    
    def start(self):
        """Start the weather station (no API server in this build)."""
        self.logger.info("Starting Secure Weather Station")
        
        # Secure boot verification
        if not self.verify_secure_boot():
            self.logger.error("Secure boot verification failed. Exiting.")
            if not self.settings.DEBUG:
                sys.exit(1)

        # Start data collection
        self.running = True
        self.data_thread = threading.Thread(target=self.data_collection_loop)
        self.data_thread.daemon = True
        self.data_thread.start()

        # Keep the main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self._signal_handler(signal.SIGINT, None)
            """Start the weather station"""
            self.logger.info("Starting Secure Weather Station")
            
            # Verify secure boot
            if not self.verify_secure_boot():
                self.logger.error("Secure boot verification failed. Exiting.")
                if not self.settings.DEBUG:
                    sys.exit(1)
            
            # Start data collection thread
            self.running = True
            self.data_thread = threading.Thread(target=self.data_collection_loop)
            self.data_thread.daemon = True
            self.data_thread.start()
            
            # Start API server
            api_app = create_api_server(self)
            
            try:
                # Run with TLS if certificates are available
                if os.path.exists(self.settings.CERT_FILE):
                    api_app.run(
                        host='0.0.0.0',
                        port=self.settings.API_PORT,
                        ssl_context=(self.settings.CERT_FILE, self.settings.PRIVATE_KEY_FILE),
                        debug=False
                    )
                else:
                    self.logger.warning("Running API without TLS - development only!")
                    api_app.run(
                        host='0.0.0.0',
                        port=self.settings.API_PORT,
                        debug=self.settings.DEBUG
                    )
            except Exception as e:
                self.logger.error(f"Failed to start API server: {e}")
                self.stop()
    
    def stop(self):
        """Stop the weather station"""
        self.logger.info("Stopping Secure Weather Station")
        self.running = False
        
        if self.data_thread:
            self.data_thread.join(timeout=5)
        
        # Cleanup
        self.sensor_reader.cleanup()
        self.credential_store.cleanup()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down")
        self.stop()
        sys.exit(0)
    
    def get_status(self) -> Dict:
        """Get current station status"""
        return {
            'running': self.running,
            'device_id': self.settings.DEVICE_ID,
            'location': self.settings.LOCATION,
            'buffer_size': len(self.data_buffer),
            'last_reading': self.data_buffer[-1] if self.data_buffer else None,
            'uptime': self._get_uptime()
        }
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return f"{days}d {hours}h {minutes}m"
        except Exception:
            return "unknown"


def main():
    """Main entry point"""
    # Check if running as root (not recommended)
    if os.geteuid() == 0:
        print("Warning: Running as root is not recommended for security reasons")
        print("Consider running as a dedicated user with appropriate permissions")
    
    # Create and start weather station
    station = SecureWeatherStation()
    
    try:
        station.start()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
        station.stop()
    except Exception as e:
        print(f"Fatal error: {e}")
        station.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()