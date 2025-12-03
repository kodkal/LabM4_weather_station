#!/usr/bin/env python3
"""
Simulation Mode Test Script
Demonstrates weather station operation without physical sensors
"""

import sys
import os
import time
import json
from datetime import datetime

# Add project root to path
#sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Force simulation mode for this test
os.environ['SENSOR_SIMULATION'] = 'true'
os.environ['DEBUG'] = 'true'

from sensor_module import SensorReader, WeatherPattern
from encryption import SecureDataTransmission
from validation import InputValidator, DataType

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_basic_simulation():
    """Test basic sensor simulation"""
    print_header("BASIC SIMULATION TEST")
    
    sensor = SensorReader(sensor_type="SIMULATED")
    
    print(f"Sensor Type: {sensor.sensor_type}")
    print(f"Is Simulated: {sensor.is_simulated}")
    
    # Read 5 samples
    print("\nReading sensor data (5 samples):")
    for i in range(5):
        data = sensor.read_sensor()
        if data:
            print(f"\n Sample {i+1}:")
            print(f"  Temperature: {data['temperature']}°C")
            print(f"  Humidity: {data['humidity']}%")
            print(f"  Pressure: {data['pressure']} hPa")
            print(f"  Pattern: {data.get('weather_pattern', 'N/A')}")
        time.sleep(1)

def test_weather_patterns():
    """Test different weather patterns"""
    print_header("WEATHER PATTERNS TEST")
    
    patterns = [
        WeatherPattern.SUNNY,
        WeatherPattern.RAINY,
        WeatherPattern.STORMY
    ]
    
    for pattern in patterns:
        sensor = SensorReader(
            sensor_type="SIMULATED",
            simulation_config={
                'pattern': pattern,
                'location': 'utah',
                'enable_anomalies': False
            }
        )
        
        print(f"\n{pattern.value.upper()} Pattern:")
        data = sensor.read_sensor()
        if data:
            print(f"  Temperature: {data['temperature']}°C")
            print(f"  Humidity: {data['humidity']}%")
            print(f"  Pressure: {data['pressure']} hPa")

def test_anomaly_detection():
    """Test anomaly generation and detection"""
    print_header("ANOMALY DETECTION TEST")
    
    # Create sensor with anomalies enabled
    sensor = SensorReader(
        sensor_type="SIMULATED",
        simulation_config={
            'enable_anomalies': True,
            'location': 'default'
        }
    )
    
    print("Reading data with anomalies enabled...")
    print("(May take several readings to see an anomaly)")
    
    anomaly_found = False
    for i in range(50):  # Try up to 50 times
        data = sensor.read_sensor()
        if data and data.get('anomaly_detected'):
            print(f"\n✓ Anomaly detected at reading {i+1}!")
            print(f"  Temperature: {data['temperature']}°C")
            print(f"  Humidity: {data['humidity']}%")
            anomaly_found = True
            break
        time.sleep(0.1)
    
    if not anomaly_found:
        print("\nNo anomalies detected (this is random, try again)")

def test_security_features():
    """Test that security features work with simulated data"""
    print_header("SECURITY FEATURES TEST")
    
    sensor = SensorReader(sensor_type="SIMULATED")
    data = sensor.read_sensor()
    
    if not data:
        print("Failed to read sensor data")
        return
    
    # Test 1: Input Validation
    print("\n1. Input Validation:")
    validator = InputValidator()
    
    # Valid data should pass
    is_valid = validator.validate_sensor_data(data)
    print(f"  Valid sensor data: {'✓ PASS' if is_valid else '✗ FAIL'}")
    
    # Invalid data should fail
    invalid_data = {'temperature': 1000, 'humidity': -50}
    is_valid = validator.validate_sensor_data(invalid_data)
    print(f"  Invalid data rejected: {'✓ PASS' if not is_valid else '✗ FAIL'}")
    
    # Test 2: Data Encryption
    print("\n2. Data Encryption:")
    try:
        encryptor = SecureDataTransmission()
        
        # Encrypt the data
        encrypted = encryptor.encrypt_data(data)
        print(f"  Original size: {len(json.dumps(data))} bytes")
        print(f"  Encrypted size: {len(encrypted)} bytes")
        print(f"  Encrypted (first 50 chars): {encrypted[:50]}...")
        
        # Decrypt and verify
        decrypted = encryptor.decrypt_data(encrypted)
        print(f"  Decryption successful: ✓ PASS")
        
        # Verify data integrity
        matches = all(
            decrypted.get(key) == data.get(key)
            for key in ['temperature', 'humidity', 'pressure']
            if key in data
        )
        print(f"  Data integrity verified: {'✓ PASS' if matches else '✗ FAIL'}")
        
    except Exception as e:
        print(f"  Encryption test failed: {e}")

def test_auto_detection():
    """Test AUTO mode falls back to simulation"""
    print_header("AUTO DETECTION TEST")
    
    # AUTO mode should detect no hardware and use simulation
    sensor = SensorReader(sensor_type="AUTO")
    
    print(f"Sensor Type Selected: {sensor.sensor_type}")
    print(f"Is Simulated: {sensor.is_simulated}")
    
    data = sensor.read_sensor()
    if data:
        print(f"\n✓ AUTO mode successfully fell back to simulation")
        print(f"  Temperature: {data['temperature']}°C")
        print(f"  Simulated flag: {data.get('is_simulated', False)}")
    else:
        print("\n✗ AUTO mode failed to initialize")

def test_performance():
    """Test simulation performance"""
    print_header("PERFORMANCE TEST")
    
    sensor = SensorReader(sensor_type="SIMULATED")
    
    print("Testing read performance (100 reads)...")
    start_time = time.time()
    
    successful_reads = 0
    for _ in range(100):
        data = sensor.read_sensor()
        if data:
            successful_reads += 1
    
    elapsed = time.time() - start_time
    
    print(f"\nResults:")
    print(f"  Total reads: 100")
    print(f"  Successful: {successful_reads}")
    print(f"  Time elapsed: {elapsed:.2f} seconds")
    print(f"  Average time per read: {(elapsed/100)*1000:.2f} ms")
    print(f"  Success rate: {successful_reads}%")

def main():
    """Run all simulation tests"""
    print("\n" + "=" * 60)
    print(" WEATHER STATION SIMULATION MODE TEST SUITE")
    print("=" * 60)
    print("\nThis script demonstrates that the weather station")
    print("can operate fully without physical sensors.")
    
    tests = [
        ("Basic Simulation", test_basic_simulation),
        ("Weather Patterns", test_weather_patterns),
        ("Anomaly Detection", test_anomaly_detection),
        ("Security Features", test_security_features),
        ("Auto Detection", test_auto_detection),
        ("Performance", test_performance)
    ]
    
    print(f"\nRunning {len(tests)} tests...")
    
    for name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n✗ {name} failed: {e}")
    
    print("\n" + "=" * 60)
    print(" TEST SUITE COMPLETE")
    print("=" * 60)
    print("\nSimulation mode allows you to:")
    print("  ✓ Complete the entire project without sensors")
    print("  ✓ Test all security features")
    print("  ✓ Develop on any computer")
    print("  ✓ Generate realistic weather data")
    print("  ✓ Test edge cases and anomalies")

if __name__ == "__main__":
    main()