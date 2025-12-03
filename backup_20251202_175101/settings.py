"""
Configuration Settings for Secure Weather Station
Supports both hardware sensors and simulation mode
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SENSOR CONFIGURATION
# ============================================

# Sensor Settings
SENSOR_TYPE = os.environ.get('SENSOR_TYPE', 'AUTO')
SENSOR_PIN = int(os.environ.get('SENSOR_PIN', '4'))
READING_INTERVAL = int(os.environ.get('READING_INTERVAL', '60'))

# Simulation Settings
SENSOR_SIMULATION = os.environ.get('SENSOR_SIMULATION', 'false').lower() == 'true'
SIMULATION_LOCATION = os.environ.get('SIMULATION_LOCATION', 'utah')
SIMULATION_PATTERN = os.environ.get('SIMULATION_PATTERN', '')
SIMULATION_ANOMALIES = os.environ.get('SIMULATION_ANOMALIES', 'false').lower() == 'true'

# Build simulation configuration dictionary
SIMULATION_CONFIG = {
    'location': SIMULATION_LOCATION,
    'enable_anomalies': SIMULATION_ANOMALIES
}

# Add pattern if specified
if SIMULATION_PATTERN:
    from sensor_module import WeatherPattern
    try:
        SIMULATION_CONFIG['pattern'] = WeatherPattern[SIMULATION_PATTERN.upper()]
    except KeyError:
        print(f"Warning: Unknown weather pattern '{SIMULATION_PATTERN}', using random")

# ============================================
# SECURITY CONFIGURATION
# ============================================

# Security Settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'development-only-key-change-in-production')
JWT_SECRET = os.environ.get('JWT_SECRET', SECRET_KEY)
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

# Validate security keys in production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
if not DEBUG:
    if SECRET_KEY == 'development-only-key-change-in-production':
        raise ValueError("SECRET_KEY must be set in production!")
    if len(SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters!")

# ============================================
# DEVICE CONFIGURATION
# ============================================

# Device Settings
DEVICE_ID = os.environ.get('DEVICE_ID', 'weather-001')
LOCATION = os.environ.get('LOCATION', 'Unknown')

# ============================================
# API CONFIGURATION
# ============================================

# API Settings
API_PORT = int(os.environ.get('API_PORT', '8443'))
API_HOST = os.environ.get('API_HOST', '0.0.0.0')
RATE_LIMIT = int(os.environ.get('RATE_LIMIT', '60'))

# ============================================
# CERTIFICATE CONFIGURATION
# ============================================

# Certificate Settings
CERT_FILE = os.path.join(BASE_DIR, os.environ.get('CERT_FILE', 'keys/certificate.crt'))
PRIVATE_KEY_FILE = os.path.join(BASE_DIR, os.environ.get('PRIVATE_KEY_FILE', 'keys/private.key'))
CA_CERT_FILE = os.path.join(BASE_DIR, os.environ.get('CA_CERT_FILE', 'keys/ca.crt'))
KEY_FILE = os.path.join(BASE_DIR, 'keys/master.key')

# ============================================
# DATABASE CONFIGURATION
# ============================================

# Database Settings
DB_PATH = os.path.join(BASE_DIR, os.environ.get('DB_PATH', 'data/weather.db'))
CREDENTIAL_DB = os.path.join(BASE_DIR, os.environ.get('CREDENTIAL_DB', 'data/credentials.db'))

# ============================================
# LOGGING CONFIGURATION
# ============================================

# Logging Settings
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, os.environ.get('LOG_FILE', 'logs/weather_station.log'))
VERBOSE = os.environ.get('VERBOSE', 'false').lower() == 'true'

# ============================================
# PERFORMANCE CONFIGURATION
# ============================================

# Performance Settings
MAX_BUFFER_SIZE = int(os.environ.get('MAX_BUFFER_SIZE', '100'))
HISTORY_SIZE = int(os.environ.get('HISTORY_SIZE', '1000'))

# ============================================
# DEVELOPMENT CONFIGURATION
# ============================================

# Development Settings
DEV_MODE = os.environ.get('DEV_MODE', 'false').lower() == 'true'
ALLOW_INSECURE = os.environ.get('ALLOW_INSECURE', 'false').lower() == 'true'

# ============================================
# CONFIGURATION VALIDATION
# ============================================

def validate_configuration():
    """Validate configuration settings"""
    errors = []
    warnings = []
    
    # Check sensor configuration
    if SENSOR_TYPE not in ['AUTO', 'BME280', 'DHT22', 'SIMULATED']:
        warnings.append(f"Unknown sensor type: {SENSOR_TYPE}, will use AUTO")
    
    # Check if forcing simulation
    if SENSOR_SIMULATION:
        warnings.append("Simulation mode is forced via SENSOR_SIMULATION=true")
    
    # Security warnings
    if DEBUG:
        warnings.append("Debug mode is enabled - disable in production!")
    
    if ALLOW_INSECURE:
        warnings.append("Insecure connections allowed - disable in production!")
    
    # Check paths exist
    required_dirs = [
        os.path.dirname(LOG_FILE),
        os.path.dirname(DB_PATH),
        os.path.dirname(KEY_FILE)
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {dir_path}: {e}")
    
    return errors, warnings

def print_configuration():
    """Print current configuration (for debugging)"""
    if VERBOSE or DEBUG:
        print("=" * 50)
        print("WEATHER STATION CONFIGURATION")
        print("=" * 50)
        print(f"Device ID: {DEVICE_ID}")
        print(f"Location: {LOCATION}")
        print(f"Sensor Type: {SENSOR_TYPE}")
        print(f"Simulation Mode: {SENSOR_SIMULATION}")
        if SENSOR_SIMULATION:
            print(f"  - Location: {SIMULATION_LOCATION}")
            print(f"  - Anomalies: {SIMULATION_ANOMALIES}")
            print(f"  - Pattern: {SIMULATION_PATTERN or 'Random'}")
        print(f"Debug Mode: {DEBUG}")
        print(f"API Port: {API_PORT}")
        print(f"Reading Interval: {READING_INTERVAL}s")
        print("=" * 50)

# Validate configuration on import
errors, warnings = validate_configuration()

if errors:
    for error in errors:
        print(f"ERROR: {error}")
    raise Exception("Configuration errors detected")

if warnings and (VERBOSE or DEBUG):
    for warning in warnings:
        print(f"WARNING: {warning}")

# Print configuration in debug/verbose mode
if VERBOSE or DEBUG:
    print_configuration()