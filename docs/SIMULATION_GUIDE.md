# Simulation Mode Guide
## Using the Weather Station Without Physical Sensors

---

## Overview

The Secure Weather Station includes a comprehensive simulation mode that allows you to complete the entire project without physical sensors. This is perfect for:
- Students who only have a Raspberry Pi
- Development and testing on a regular computer
- Learning the security concepts without hardware investment
- Testing edge cases and anomalies

---

## Quick Start

### Option 1: Environment Variable (Easiest)
```bash
# Force simulation mode
export SENSOR_SIMULATION=true

# Run the weather station
python src/weather_station.py
```

### Option 2: Configuration File
Edit your `.env` file:
```bash
SENSOR_TYPE=SIMULATED
SENSOR_SIMULATION=true
SIMULATION_LOCATION=utah
```

### Option 3: Auto-Detection
Set `SENSOR_TYPE=AUTO` and the system will automatically use simulation if no hardware is detected.

---

## Simulation Features

### 1. Realistic Weather Patterns
The simulator generates realistic weather data with:
- **Daily temperature cycles**: Temperature rises during the day, falls at night
- **Weather patterns**: Sunny, cloudy, rainy, stormy, cold fronts, heat waves
- **Smooth transitions**: Values change gradually, not randomly
- **Correlated data**: Humidity inversely correlates with temperature

### 2. Weather Pattern Behaviors

| Pattern | Temperature Effect | Humidity Effect | Pressure Effect | Duration |
|---------|-------------------|-----------------|-----------------|----------|
| **Sunny** | +3°C | -10% | +5 hPa | 1-4 hours |
| **Cloudy** | -1°C | +5% | -2 hPa | 1-4 hours |
| **Rainy** | -3°C | +25% | -8 hPa | 1-4 hours |
| **Stormy** | -5°C | +30% | -15 hPa | 1-4 hours |
| **Cold Front** | -8°C | -5% | +10 hPa | 1-4 hours |
| **Heat Wave** | +8°C | -15% | -3 hPa | 1-4 hours |

### 3. Location-Based Base Values

| Location | Base Temp | Base Humidity | Base Pressure |
|----------|-----------|---------------|---------------|
| **Default** | 22°C | 50% | 1013.25 hPa |
| **Utah** | 18°C | 35% | 1020.0 hPa |
| **Tropical** | 28°C | 75% | 1012.0 hPa |
| **Arctic** | -5°C | 60% | 1015.0 hPa |
| **Desert** | 32°C | 20% | 1018.0 hPa |

---

## Configuration Options

### Basic Configuration
```python
# In your code
from sensor_module import SensorReader

# Basic simulation
sensor = SensorReader(sensor_type="SIMULATED")

# With specific location
sensor = SensorReader(
    sensor_type="SIMULATED",
    simulation_config={
        'location': 'utah',
        'pattern': WeatherPattern.SUNNY,
        'enable_anomalies': False
    }
)
```

### Advanced Configuration
```python
# Testing with anomalies
sensor = SensorReader(
    sensor_type="SIMULATED",
    simulation_config={
        'location': 'utah',
        'enable_anomalies': True,  # Random spikes/drops
        'pattern': WeatherPattern.STORMY
    }
)

# Access the simulator directly
if sensor.is_simulated:
    # Change weather pattern mid-run
    sensor.sensor.set_weather_pattern(WeatherPattern.RAINY)
    
    # Get simulation status
    status = sensor.sensor.get_status()
    print(f"Current pattern: {status['current_pattern']}")
```

---

## Testing Scenarios

### 1. Normal Operation
```bash
# Standard weather simulation
SENSOR_TYPE=SIMULATED python src/weather_station.py
```

### 2. Testing Anomaly Detection
```bash
# Enable anomalies to test your detection code
SENSOR_SIMULATION=true SIMULATION_ANOMALIES=true python src/weather_station.py
```

### 3. Specific Weather Patterns
```python
# In test code
def test_storm_conditions():
    sensor = SensorReader(
        sensor_type="SIMULATED",
        simulation_config={'pattern': WeatherPattern.STORMY}
    )
    
    data = sensor.read_sensor()
    assert data['pressure'] < 1000  # Low pressure in storms
    assert data['humidity'] > 70     # High humidity
```

### 4. Testing Encryption Overhead
```python
# Generate consistent data for performance testing
sensor = SensorReader(
    sensor_type="SIMULATED",
    simulation_config={
        'pattern': WeatherPattern.SUNNY,  # Stable pattern
        'enable_anomalies': False
    }
)
```

---

## Development Workflow

### Local Development (No Pi Required)
```bash
# 1. Clone repository on your computer
git clone https://github.com/yourrepo/secure-weather-station.git

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies (skip RPi-specific ones)
pip install flask flask-cors pyjwt cryptography python-dotenv

# 4. Run in simulation mode
export SENSOR_SIMULATION=true
export DEBUG=true
python src/weather_station.py

# 5. Access API at https://localhost:8443
```

### Testing Security Features
The simulation mode allows you to test ALL security features:
- ✅ **Secure Boot**: File integrity checks work the same
- ✅ **Encryption**: Data is encrypted regardless of source
- ✅ **JWT Authentication**: API security is identical
- ✅ **Input Validation**: Simulated data goes through same validation
- ✅ **Credential Storage**: Works exactly the same

---

## Identifying Simulated Data

Simulated data includes markers to identify it:
```json
{
    "temperature": 22.5,
    "humidity": 48.3,
    "pressure": 1013.2,
    "altitude": 124.5,
    "timestamp": "2024-11-18T10:30:00Z",
    "sensor_type": "SIMULATED",
    "is_simulated": true,
    "weather_pattern": "sunny",
    "simulated": true
}
```

---

## Common Use Cases

### 1. Student Without Sensors
```bash
# Complete the entire project with simulation
echo "SENSOR_SIMULATION=true" >> .env
echo "SIMULATION_LOCATION=utah" >> .env
```

### 2. Testing at Home
```bash
# Develop on your laptop before deploying to Pi
SENSOR_SIMULATION=true python src/weather_station.py
```

### 3. Demonstrating Security Vulnerabilities
```python
# Generate anomalous data to test detection
sensor = SensorReader(
    sensor_type="SIMULATED",
    simulation_config={'enable_anomalies': True}
)
```

### 4. Load Testing
```bash
# Consistent data for performance testing
SENSOR_TYPE=SIMULATED SIMULATION_ANOMALIES=false python scripts/stress_test.py
```

---

## Advantages of Simulation Mode

1. **No Hardware Required**: Complete the project with just software
2. **Consistent Testing**: Reproducible data for debugging
3. **Edge Case Testing**: Test anomalies and extreme weather
4. **Rapid Development**: No hardware setup delays
5. **Cross-Platform**: Develop on Windows/Mac/Linux
6. **Cost-Effective**: No sensor purchase required

---

## Transitioning to Real Sensors

When you're ready to use real sensors:

1. **Connect your sensor** (see wiring guide)
2. **Change configuration**:
   ```bash
   SENSOR_TYPE=AUTO  # Auto-detects hardware
   SENSOR_SIMULATION=false
   ```
3. **Restart the application**

The security features work identically with real or simulated data!

---

## Troubleshooting

### Simulation Not Working
```bash
# Check if simulation is enabled
echo $SENSOR_SIMULATION

# Check Python can find the module
python -c "from sensor_module import SimulatedSensor"
```

### Data Seems Random
- Simulated data has realistic variations
- Check `enable_anomalies` is false for stable data
- Weather patterns change every 1-4 hours by design

### Performance Issues
```python
# Reduce reading frequency for testing
READING_INTERVAL=5  # Read every 5 seconds instead of 60
```

---

## Example Test Script

```python
#!/usr/bin/env python3
"""Test script using simulation mode"""

import time
from sensor_module import SensorReader, WeatherPattern

def test_all_patterns():
    """Test each weather pattern"""
    sensor = SensorReader(sensor_type="SIMULATED")
    
    patterns = [
        WeatherPattern.SUNNY,
        WeatherPattern.CLOUDY,
        WeatherPattern.RAINY,
        WeatherPattern.STORMY,
        WeatherPattern.COLD_FRONT,
        WeatherPattern.HEAT_WAVE
    ]
    
    for pattern in patterns:
        print(f"\n Testing {pattern.value} pattern:")
        sensor.sensor.set_weather_pattern(pattern)
        
        for _ in range(3):
            data = sensor.read_sensor()
            print(f"  Temp: {data['temperature']}°C, "
                  f"Humidity: {data['humidity']}%, "
                  f"Pressure: {data['pressure']} hPa")
            time.sleep(1)

if __name__ == "__main__":
    test_all_patterns()
```

---

## Security Testing with Simulation

### Test Injection Attacks
```python
# Simulated data goes through same validation
malicious_data = {
    'temperature': "'; DROP TABLE sensors; --",
    'humidity': 50,
    'pressure': 1013
}
# Your validation should catch this
```

### Test Encryption
```bash
# Capture traffic to verify encryption
tcpdump -i lo -w capture.pcap port 8443
# Simulated data is encrypted the same way
```

### Test Authentication
```bash
# API security works identically
curl -X GET https://localhost:8443/api/data
# Should require JWT token regardless of data source
```

---

## Grading Note

**Using simulation mode does NOT affect your grade!** The project is about implementing security controls, not reading sensors. All security features work identically with simulated or real data.

---

## Summary

The simulation mode provides a complete, realistic alternative to physical sensors while maintaining all security learning objectives. Use it to:
- Complete the project without hardware
- Test your implementation thoroughly
- Understand security concepts
- Develop from anywhere

Remember: The security implementation is what matters, not whether your data comes from a real sensor or simulation!

---

*Simulation Mode Guide v1.0 | November 2024*