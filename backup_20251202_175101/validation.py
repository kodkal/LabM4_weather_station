"""
Input Validation Module
Implements comprehensive input validation to prevent injection attacks and ensure data integrity
"""

import re
import json
import ipaddress
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timezone
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DataType(Enum):
    """Supported data types for validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    EMAIL = "email"
    URL = "url"
    IP_ADDRESS = "ip_address"
    MAC_ADDRESS = "mac_address"
    JSON = "json"
    DATETIME = "datetime"
    SENSOR_DATA = "sensor_data"
    DEVICE_ID = "device_id"
    API_KEY = "api_key"


class InputValidator:
    """Comprehensive input validation for IoT security"""
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize input validator
        
        Args:
            strict_mode: If True, apply strictest validation rules
        """
        self.strict_mode = strict_mode
        
        # Define validation patterns
        self._init_patterns()
        
        # Define safe ranges for sensor data
        self._init_sensor_ranges()
        
        # Track validation statistics
        self.validation_stats = {
            'total_validations': 0,
            'passed': 0,
            'failed': 0,
            'blocked_injections': 0
        }
        
        logger.info(f"Input validator initialized (strict_mode={strict_mode})")
    
    def _init_patterns(self):
        """Initialize regex patterns for validation"""
        self.patterns = {
            # Basic patterns
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'url': re.compile(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'),
            'mac_address': re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'),
            'device_id': re.compile(r'^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$'),
            'api_key': re.compile(r'^[a-zA-Z0-9_-]{32,128}$'),
            
            # Security patterns (detect potential attacks)
            'sql_injection': re.compile(
                r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|'
                r'\bEXEC\b|\bEXECUTE\b|--|;|\'|\"|`|\x00|\x1a)', 
                re.IGNORECASE
            ),
            'xss_attack': re.compile(
                r'(<script|javascript:|onerror=|onload=|alert\(|document\.|window\.|eval\()',
                re.IGNORECASE
            ),
            'command_injection': re.compile(
                r'([;&|`$]|\$\(|\|\||&&|>|<|\n|\r|\\x[0-9a-f]{2})',
                re.IGNORECASE
            ),
            'path_traversal': re.compile(r'(\.\./|\.\.\\|%2e%2e|0x2e0x2e)'),
            'ldap_injection': re.compile(r'[*()\\|&=]'),
            'xml_injection': re.compile(r'(<\?xml|<!DOCTYPE|<!ENTITY|SYSTEM|PUBLIC)', re.IGNORECASE),
            'nosql_injection': re.compile(r'(\$where|\$ne|\$gt|\$lt|\$regex|\$exists)', re.IGNORECASE),
            
            # Whitelist patterns
            'alphanumeric': re.compile(r'^[a-zA-Z0-9]+$'),
            'alphanumeric_space': re.compile(r'^[a-zA-Z0-9 ]+$'),
            'safe_string': re.compile(r'^[a-zA-Z0-9\s\-_.]+$'),
            'safe_filename': re.compile(r'^[a-zA-Z0-9\-_.]+$'),
            'location_string': re.compile(r'^[a-zA-Z0-9\s\-_.,]+$')
        }
    
    def _init_sensor_ranges(self):
        """Initialize valid ranges for sensor data"""
        self.sensor_ranges = {
            'temperature': {
                'min': -50.0,   # Celsius
                'max': 60.0,
                'rate_of_change': 10.0  # Max change per reading
            },
            'humidity': {
                'min': 0.0,     # Percentage
                'max': 100.0,
                'rate_of_change': 20.0
            },
            'pressure': {
                'min': 800.0,   # hPa
                'max': 1100.0,
                'rate_of_change': 50.0
            },
            'altitude': {
                'min': -500.0,  # Meters
                'max': 9000.0,
                'rate_of_change': 100.0
            },
            'light': {
                'min': 0,       # Lux
                'max': 100000,
                'rate_of_change': 50000
            }
        }
        
        # Track last values for rate of change validation
        self.last_sensor_values = {}
    
    def validate(self, value: Any, data_type: DataType, 
                 additional_checks: Dict = None) -> Tuple[bool, Optional[str]]:
        """
        Main validation method
        
        Args:
            value: Value to validate
            data_type: Expected data type
            additional_checks: Additional validation parameters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        self.validation_stats['total_validations'] += 1
        
        try:
            # Check for None/empty values
            if value is None:
                if additional_checks and additional_checks.get('required', True):
                    raise ValidationError("Required value is missing")
                return True, None
            
            # Check for injection attempts first
            if self._detect_injection(value):
                self.validation_stats['blocked_injections'] += 1
                raise ValidationError("Potential injection attack detected")
            
            # Type-specific validation
            if data_type == DataType.STRING:
                result = self._validate_string(value, additional_checks)
            elif data_type == DataType.INTEGER:
                result = self._validate_integer(value, additional_checks)
            elif data_type == DataType.FLOAT:
                result = self._validate_float(value, additional_checks)
            elif data_type == DataType.BOOLEAN:
                result = self._validate_boolean(value)
            elif data_type == DataType.EMAIL:
                result = self._validate_email(value)
            elif data_type == DataType.URL:
                result = self._validate_url(value)
            elif data_type == DataType.IP_ADDRESS:
                result = self._validate_ip_address(value)
            elif data_type == DataType.MAC_ADDRESS:
                result = self._validate_mac_address(value)
            elif data_type == DataType.JSON:
                result = self._validate_json(value)
            elif data_type == DataType.DATETIME:
                result = self._validate_datetime(value)
            elif data_type == DataType.SENSOR_DATA:
                result = self._validate_sensor_data_comprehensive(value)
            elif data_type == DataType.DEVICE_ID:
                result = self._validate_device_id(value)
            elif data_type == DataType.API_KEY:
                result = self._validate_api_key(value)
            else:
                raise ValidationError(f"Unknown data type: {data_type}")
            
            if result:
                self.validation_stats['passed'] += 1
                return True, None
            else:
                raise ValidationError(f"Validation failed for {data_type.value}")
                
        except ValidationError as e:
            self.validation_stats['failed'] += 1
            logger.warning(f"Validation failed: {e}",
                          extra={"event": "validation_failed", 
                               "data_type": data_type.value})
            return False, str(e)
        except Exception as e:
            self.validation_stats['failed'] += 1
            logger.error(f"Validation error: {e}",
                        extra={"event": "validation_error"})
            return False, f"Validation error: {e}"
    
    def _detect_injection(self, value: Any) -> bool:
        """Detect potential injection attacks"""
        if not isinstance(value, str):
            value = str(value)
        
        # Check against injection patterns
        injection_patterns = [
            'sql_injection',
            'xss_attack',
            'command_injection',
            'path_traversal',
            'ldap_injection',
            'xml_injection',
            'nosql_injection'
        ]
        
        for pattern_name in injection_patterns:
            if self.patterns[pattern_name].search(value):
                logger.warning(f"Potential {pattern_name} detected",
                             extra={"event": "injection_detected",
                                  "type": pattern_name,
                                  "value_sample": value[:50]})
                return True
        
        return False
    
    def _validate_string(self, value: str, checks: Dict = None) -> bool:
        """Validate string input"""
        if not isinstance(value, str):
            return False
        
        if checks:
            # Check length
            if 'min_length' in checks and len(value) < checks['min_length']:
                return False
            if 'max_length' in checks and len(value) > checks['max_length']:
                return False
            
            # Check pattern
            if 'pattern' in checks:
                pattern_name = checks['pattern']
                if pattern_name in self.patterns:
                    if not self.patterns[pattern_name].match(value):
                        return False
            
            # Check allowed values
            if 'allowed_values' in checks:
                if value not in checks['allowed_values']:
                    return False
        
        # In strict mode, only allow safe strings by default
        if self.strict_mode and not checks:
            return bool(self.patterns['safe_string'].match(value))
        
        return True
    
    def _validate_integer(self, value: Any, checks: Dict = None) -> bool:
        """Validate integer input"""
        try:
            int_value = int(value)
            
            if checks:
                if 'min' in checks and int_value < checks['min']:
                    return False
                if 'max' in checks and int_value > checks['max']:
                    return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def _validate_float(self, value: Any, checks: Dict = None) -> bool:
        """Validate float input"""
        try:
            float_value = float(value)
            
            # Check for special values
            if float_value != float_value:  # NaN check
                return False
            if float_value == float('inf') or float_value == float('-inf'):
                return False
            
            if checks:
                if 'min' in checks and float_value < checks['min']:
                    return False
                if 'max' in checks and float_value > checks['max']:
                    return False
                if 'precision' in checks:
                    # Check decimal places
                    str_value = str(value)
                    if '.' in str_value:
                        decimals = len(str_value.split('.')[1])
                        if decimals > checks['precision']:
                            return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def _validate_boolean(self, value: Any) -> bool:
        """Validate boolean input"""
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.lower() in ['true', 'false', '1', '0', 'yes', 'no']
        if isinstance(value, (int, float)):
            return value in [0, 1]
        return False
    
    def _validate_email(self, value: str) -> bool:
        """Validate email address"""
        if not isinstance(value, str):
            return False
        return bool(self.patterns['email'].match(value))
    
    def _validate_url(self, value: str) -> bool:
        """Validate URL"""
        if not isinstance(value, str):
            return False
        
        # Check pattern
        if not self.patterns['url'].match(value):
            return False
        
        # Additional security checks
        if self.strict_mode:
            # Block local/private URLs
            blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.', '10.', '172.']
            for blocked in blocked_hosts:
                if blocked in value.lower():
                    return False
        
        return True
    
    def _validate_ip_address(self, value: str) -> bool:
        """Validate IP address"""
        try:
            ip = ipaddress.ip_address(value)
            
            # In strict mode, block private/reserved IPs
            if self.strict_mode:
                if ip.is_private or ip.is_reserved or ip.is_loopback:
                    return False
            
            return True
        except ValueError:
            return False
    
    def _validate_mac_address(self, value: str) -> bool:
        """Validate MAC address"""
        if not isinstance(value, str):
            return False
        return bool(self.patterns['mac_address'].match(value))
    
    def _validate_json(self, value: Union[str, dict]) -> bool:
        """Validate JSON data"""
        try:
            if isinstance(value, str):
                json.loads(value)
            elif not isinstance(value, dict):
                return False
            return True
        except json.JSONDecodeError:
            return False
    
    def _validate_datetime(self, value: Union[str, datetime]) -> bool:
        """Validate datetime"""
        if isinstance(value, datetime):
            return True
        
        if isinstance(value, str):
            # Try common datetime formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S.%fZ'
            ]
            
            for fmt in formats:
                try:
                    datetime.strptime(value, fmt)
                    return True
                except ValueError:
                    continue
        
        return False
    
    def _validate_device_id(self, value: str) -> bool:
        """Validate device ID format"""
        if not isinstance(value, str):
            return False
        
        # Check UUID format
        if self.patterns['device_id'].match(value):
            return True
        
        # Also allow alphanumeric IDs of reasonable length
        if self.patterns['alphanumeric'].match(value) and 8 <= len(value) <= 64:
            return True
        
        return False
    
    def _validate_api_key(self, value: str) -> bool:
        """Validate API key format"""
        if not isinstance(value, str):
            return False
        return bool(self.patterns['api_key'].match(value))
    
    def validate_sensor_data(self, data: Dict) -> bool:
        """
        Validate sensor data readings
        
        Args:
            data: Dictionary containing sensor readings
            
        Returns:
            True if all data is valid
        """
        try:
            return self._validate_sensor_data_comprehensive(data)
        except Exception as e:
            logger.error(f"Sensor data validation error: {e}")
            return False
    
    def _validate_sensor_data_comprehensive(self, data: Dict) -> bool:
        """Comprehensive sensor data validation"""
        if not isinstance(data, dict):
            return False
        
        valid = True
        
        for sensor_type, value in data.items():
            if sensor_type not in self.sensor_ranges:
                logger.warning(f"Unknown sensor type: {sensor_type}")
                continue
            
            ranges = self.sensor_ranges[sensor_type]
            
            # Check value range
            if not isinstance(value, (int, float)):
                logger.warning(f"Invalid sensor value type for {sensor_type}: {type(value)}")
                valid = False
                continue
            
            if value < ranges['min'] or value > ranges['max']:
                logger.warning(f"Sensor value out of range for {sensor_type}: {value}")
                valid = False
                continue
            
            # Check rate of change
            if sensor_type in self.last_sensor_values:
                last_value = self.last_sensor_values[sensor_type]
                change = abs(value - last_value)
                
                if change > ranges['rate_of_change']:
                    logger.warning(f"Suspicious rate of change for {sensor_type}: {change}")
                    if self.strict_mode:
                        valid = False
            
            # Update last value
            self.last_sensor_values[sensor_type] = value
        
        return valid
    
    def sanitize_string(self, value: str, max_length: int = 255) -> str:
        """
        Sanitize string input by removing dangerous characters
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes and control characters
        value = value.replace('\x00', '')
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        # HTML entity encoding for special characters
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;'
        }
        
        for old, new in replacements.items():
            value = value.replace(old, new)
        
        # Truncate to max length
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    def validate_api_request(self, request_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate complete API request
        
        Args:
            request_data: API request data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_fields = ['device_id', 'timestamp']
        for field in required_fields:
            if field not in request_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate each field
        if 'device_id' in request_data:
            valid, error = self.validate(request_data['device_id'], DataType.DEVICE_ID)
            if not valid:
                errors.append(f"Invalid device_id: {error}")
        
        if 'timestamp' in request_data:
            valid, error = self.validate(request_data['timestamp'], DataType.DATETIME)
            if not valid:
                errors.append(f"Invalid timestamp: {error}")
        
        if 'data' in request_data:
            if not self.validate_sensor_data(request_data['data']):
                errors.append("Invalid sensor data")
        
        return len(errors) == 0, errors
    
    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        stats = self.validation_stats.copy()
        
        if stats['total_validations'] > 0:
            stats['pass_rate'] = (stats['passed'] / stats['total_validations']) * 100
            stats['injection_rate'] = (stats['blocked_injections'] / stats['total_validations']) * 100
        else:
            stats['pass_rate'] = 0
            stats['injection_rate'] = 0
        
        return stats
    
    def reset_stats(self):
        """Reset validation statistics"""
        self.validation_stats = {
            'total_validations': 0,
            'passed': 0,
            'failed': 0,
            'blocked_injections': 0
        }
        logger.info("Validation statistics reset")


class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_history = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed based on rate limits
        
        Args:
            identifier: Unique identifier (IP, device_id, etc.)
            
        Returns:
            True if request is allowed
        """
        now = datetime.now(timezone.utc)
        
        if identifier not in self.request_history:
            self.request_history[identifier] = []
        
        # Clean old requests
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.request_history[identifier] = [
            timestamp for timestamp in self.request_history[identifier]
            if timestamp > cutoff
        ]
        
        # Check limit
        if len(self.request_history[identifier]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        self.request_history[identifier].append(now)
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Get number of remaining requests for an identifier"""
        if identifier not in self.request_history:
            return self.max_requests
        
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        active_requests = sum(
            1 for timestamp in self.request_history[identifier]
            if timestamp > cutoff
        )
        
        return max(0, self.max_requests - active_requests)