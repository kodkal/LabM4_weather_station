"""
Sensor Module for Weather Station
Interfaces with temperature, humidity, and pressure sensors
Includes comprehensive simulation mode for testing without hardware
"""

import os
import sys
import time
import random
import math
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)

# Check if we should force simulation mode
FORCE_SIMULATION = os.environ.get('SENSOR_SIMULATION', 'false').lower() == 'true'

# Detect if we're on a Raspberry Pi
def is_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            return 'Raspberry Pi' in model
    except:
        return False

IS_RASPBERRY_PI = is_raspberry_pi()

# Initialize hardware availability flag
HARDWARE_AVAILABLE = False

# Try to import hardware libraries (only on Raspberry Pi and if not forcing simulation)
if not FORCE_SIMULATION and IS_RASPBERRY_PI:
    try:
        import board
        import adafruit_bme280.advanced as adafruit_bme280
        import adafruit_dht
        import RPi.GPIO as GPIO
        HARDWARE_AVAILABLE = True
        logger.info("Hardware libraries loaded successfully")
    except ImportError as e:
        logger.warning(f"Hardware libraries not available: {e}")
        logger.info("Falling back to simulation mode")
        HARDWARE_AVAILABLE = False
else:
    if FORCE_SIMULATION:
        logger.info("Simulation mode forced via SENSOR_SIMULATION environment variable")
    elif not IS_RASPBERRY_PI:
        logger.info("Not running on Raspberry Pi - using simulation mode")
    HARDWARE_AVAILABLE = False


class WeatherPattern(Enum):
    """Weather patterns for realistic simulation"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    COLD_FRONT = "cold_front"
    HEAT_WAVE = "heat_wave"


class SensorInterface(ABC):
    """Abstract base class for sensor interfaces"""
    
    @abstractmethod
    def read(self) -> Dict[str, float]:
        """Read sensor data"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up sensor resources"""
        pass
    
    @abstractmethod
    def validate_reading(self, data: Dict[str, float]) -> bool:
        """Validate sensor reading"""
        pass


class BME280Sensor(SensorInterface):
    """BME280 Temperature, Humidity, and Pressure Sensor"""
    
    def __init__(self, i2c_address: int = 0x77):
        """Initialize BME280 sensor"""
        if not HARDWARE_AVAILABLE:
            raise RuntimeError("BME280 hardware not available. Use SIMULATED sensor type.")
        
        self.address = i2c_address
        self.sensor = None
        
        try:
            import busio
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=i2c_address)
            
            # Configure sensor for weather monitoring
            self.sensor.mode = adafruit_bme280.MODE_NORMAL
            self.sensor.standby_period = adafruit_bme280.STANDBY_TC_500
            self.sensor.iir_filter = adafruit_bme280.IIR_FILTER_X16
            self.sensor.overscan_pressure = adafruit_bme280.OVERSCAN_X16
            self.sensor.overscan_humidity = adafruit_bme280.OVERSCAN_X2
            self.sensor.overscan_temperature = adafruit_bme280.OVERSCAN_X2
            
            logger.info(f"BME280 sensor initialized at address 0x{i2c_address:02x}")
        except Exception as e:
            logger.error(f"Failed to initialize BME280: {e}")
            raise
    
    def read(self) -> Dict[str, float]:
        """Read data from BME280 sensor"""
        try:
            data = {
                'temperature': round(self.sensor.temperature, 2),
                'humidity': round(self.sensor.humidity, 2),
                'pressure': round(self.sensor.pressure, 2),
                'altitude': round(self.sensor.altitude, 2),
                'timestamp': datetime.now().isoformat(),
                'sensor_type': 'BME280'
            }
            return data
        except Exception as e:
            logger.error(f"Error reading BME280: {e}")
            return {}
    
    def cleanup(self):
        """Clean up BME280 resources"""
        # BME280 doesn't require cleanup
        pass
    
    def validate_reading(self, data: Dict[str, float]) -> bool:
        """Validate BME280 reading"""
        if not data:
            return False
        
        # Validate temperature (-40 to 85°C for BME280)
        if not (-40 <= data.get('temperature', 0) <= 85):
            logger.warning(f"Temperature out of range: {data.get('temperature')}")
            return False
        
        # Validate humidity (0 to 100%)
        if not (0 <= data.get('humidity', 0) <= 100):
            logger.warning(f"Humidity out of range: {data.get('humidity')}")
            return False
        
        # Validate pressure (300 to 1100 hPa)
        if not (300 <= data.get('pressure', 0) <= 1100):
            logger.warning(f"Pressure out of range: {data.get('pressure')}")
            return False
        
        return True


class DHT22Sensor(SensorInterface):
    """DHT22 Temperature and Humidity Sensor"""
    
    def __init__(self, pin: int = 4):
        """Initialize DHT22 sensor"""
        if not HARDWARE_AVAILABLE:
            raise RuntimeError("DHT22 hardware not available. Use SIMULATED sensor type.")
        
        self.pin = pin
        self.dht_device = None
        
        try:
            dht_pin = getattr(board, f'D{pin}')
            self.dht_device = adafruit_dht.DHT22(dht_pin)
            logger.info(f"DHT22 sensor initialized on GPIO {pin}")
        except Exception as e:
            logger.error(f"Failed to initialize DHT22: {e}")
            raise
    
    def read(self) -> Dict[str, float]:
        """Read data from DHT22 sensor"""
        try:
            temperature = self.dht_device.temperature
            humidity = self.dht_device.humidity
            
            if temperature is not None and humidity is not None:
                data = {
                    'temperature': round(temperature, 2),
                    'humidity': round(humidity, 2),
                    'timestamp': datetime.now().isoformat(),
                    'sensor_type': 'DHT22'
                }
                return data
            else:
                logger.warning("DHT22 returned None values")
                return {}
        except RuntimeError as e:
            # DHT sensors often have temporary read failures
            logger.debug(f"DHT22 read error (expected occasionally): {e}")
            return {}
        except Exception as e:
            logger.error(f"Error reading DHT22: {e}")
            return {}
    
    def cleanup(self):
        """Clean up DHT22 resources"""
        if self.dht_device:
            self.dht_device.exit()
    
    def validate_reading(self, data: Dict[str, float]) -> bool:
        """Validate DHT22 reading"""
        if not data:
            return False
        
        # Validate temperature (-40 to 80°C for DHT22)
        if not (-40 <= data.get('temperature', 0) <= 80):
            logger.warning(f"Temperature out of range: {data.get('temperature')}")
            return False
        
        # Validate humidity (0 to 100%)
        if not (0 <= data.get('humidity', 0) <= 100):
            logger.warning(f"Humidity out of range: {data.get('humidity')}")
            return False
        
        return True


class SimulatedSensor(SensorInterface):
    """Simulated sensor for testing and development"""
    
    def __init__(self, location: str = "utah", enable_anomalies: bool = False):
        """
        Initialize simulated sensor
        
        Args:
            location: Location for weather simulation (affects base values)
            enable_anomalies: Whether to inject anomalous readings for testing
        """
        self.location = location.lower()
        self.enable_anomalies = enable_anomalies
        
        # Base values for different locations
        self.location_bases = {
            'utah': {'temp': 15.0, 'humidity': 40.0, 'pressure': 1013.25, 'altitude': 1400},
            'seattle': {'temp': 12.0, 'humidity': 70.0, 'pressure': 1013.25, 'altitude': 50},
            'miami': {'temp': 25.0, 'humidity': 75.0, 'pressure': 1013.25, 'altitude': 2},
            'denver': {'temp': 10.0, 'humidity': 35.0, 'pressure': 835.0, 'altitude': 1609},
        }
        
        # Get base values for location (default to Utah)
        self.base = self.location_bases.get(self.location, self.location_bases['utah'])
        
        # Current weather pattern
        self.current_pattern = WeatherPattern.SUNNY
        self.pattern_start_time = datetime.now()
        self.pattern_duration = timedelta(hours=random.uniform(1, 4))
        
        # Trend tracking for smooth transitions
        self.temperature_trend = 0.0
        self.humidity_trend = 0.0
        self.pressure_trend = 0.0
        
        logger.info(f"Simulated sensor initialized (Location: {location}, Anomalies: {enable_anomalies})")
    
    def _get_time_of_day_factor(self) -> float:
        """Calculate temperature factor based on time of day"""
        hour = datetime.now().hour
        # Temperature peaks at 2 PM (14:00), lowest at 5 AM (5:00)
        # Using sine wave: peak at hour 14, trough at hour 5
        angle = (hour - 5) * (2 * math.pi / 24)
        return math.sin(angle)
    
    def _update_weather_pattern(self):
        """Update weather pattern if duration has elapsed"""
        if datetime.now() - self.pattern_start_time > self.pattern_duration:
            # Choose new pattern
            patterns = list(WeatherPattern)
            self.current_pattern = random.choice(patterns)
            self.pattern_start_time = datetime.now()
            self.pattern_duration = timedelta(hours=random.uniform(1, 4))
            logger.info(f"Weather pattern changed to: {self.current_pattern.value}")
    
    def _get_pattern_effects(self) -> Dict[str, float]:
        """Get the effects of current weather pattern"""
        effects = {
            WeatherPattern.SUNNY: {'temp': 3.0, 'humidity': -10.0, 'pressure': 5.0},
            WeatherPattern.CLOUDY: {'temp': -1.0, 'humidity': 5.0, 'pressure': -2.0},
            WeatherPattern.RAINY: {'temp': -3.0, 'humidity': 25.0, 'pressure': -8.0},
            WeatherPattern.STORMY: {'temp': -5.0, 'humidity': 30.0, 'pressure': -15.0},
            WeatherPattern.COLD_FRONT: {'temp': -8.0, 'humidity': -5.0, 'pressure': 10.0},
            WeatherPattern.HEAT_WAVE: {'temp': 8.0, 'humidity': -15.0, 'pressure': -3.0},
        }
        return effects.get(self.current_pattern, {'temp': 0, 'humidity': 0, 'pressure': 0})
    
    def _add_noise(self, value: float, noise_level: float = 0.5) -> float:
        """Add random noise to a value"""
        return value + random.uniform(-noise_level, noise_level)
    
    def _generate_anomaly(self) -> Optional[Dict[str, float]]:
        """Generate anomalous reading (for testing detection systems)"""
        if not self.enable_anomalies or random.random() > 0.05:  # 5% chance
            return None
        
        anomaly_type = random.choice(['spike', 'dropout', 'stuck'])
        
        if anomaly_type == 'spike':
            return {
                'temperature': self.base['temp'] + random.uniform(20, 50),
                'humidity': min(100, self.base['humidity'] + random.uniform(30, 50)),
                'pressure': self.base['pressure'] + random.uniform(50, 100),
                'anomaly': 'spike'
            }
        elif anomaly_type == 'dropout':
            return {
                'temperature': -999,
                'humidity': -999,
                'pressure': -999,
                'anomaly': 'dropout'
            }
        else:  # stuck
            return {
                'temperature': self.base['temp'],
                'humidity': self.base['humidity'],
                'pressure': self.base['pressure'],
                'anomaly': 'stuck'
            }
    
    def read(self) -> Dict[str, float]:
        """Generate simulated sensor data"""
        # Update weather pattern
        self._update_weather_pattern()
        
        # Check for anomaly
        if self.enable_anomalies:
            anomaly = self._generate_anomaly()
            if anomaly:
                anomaly['timestamp'] = datetime.now().isoformat()
                anomaly['sensor_type'] = 'SIMULATED'
                anomaly['is_simulated'] = True
                return anomaly
        
        # Get time of day effect
        tod_factor = self._get_time_of_day_factor()
        tod_temp_effect = tod_factor * 5.0  # ±5°C daily variation
        
        # Get weather pattern effects
        pattern_effects = self._get_pattern_effects()
        
        # Calculate values with smooth trends
        temperature = self.base['temp'] + tod_temp_effect + pattern_effects['temp']
        temperature = self._add_noise(temperature, 0.5)
        self.temperature_trend = self.temperature_trend * 0.9 + temperature * 0.1
        
        humidity = self.base['humidity'] + pattern_effects['humidity']
        # Humidity inversely correlates with temperature
        humidity -= tod_factor * 5.0
        humidity = max(0, min(100, self._add_noise(humidity, 2.0)))
        self.humidity_trend = self.humidity_trend * 0.9 + humidity * 0.1
        
        pressure = self.base['pressure'] + pattern_effects['pressure']
        pressure = self._add_noise(pressure, 1.0)
        self.pressure_trend = self.pressure_trend * 0.9 + pressure * 0.1
        
        # Calculate altitude from pressure
        altitude = 44330 * (1 - (pressure / 1013.25) ** 0.1903)
        
        data = {
            'temperature': round(self.temperature_trend, 2),
            'humidity': round(self.humidity_trend, 2),
            'pressure': round(self.pressure_trend, 2),
            'altitude': round(altitude, 2),
            'timestamp': datetime.now().isoformat(),
            'sensor_type': 'SIMULATED',
            'is_simulated': True,
            'weather_pattern': self.current_pattern.value,
            'location': self.location
        }
        
        return data
    
    def cleanup(self):
        """Clean up simulated sensor (no-op)"""
        pass
    
    def validate_reading(self, data: Dict[str, float]) -> bool:
        """Validate simulated reading"""
        if not data:
            return False
        
        # Allow anomalous readings through
        if data.get('anomaly'):
            return True
        
        # Standard validation
        if not (-50 <= data.get('temperature', 0) <= 60):
            return False
        if not (0 <= data.get('humidity', 0) <= 100):
            return False
        if not (300 <= data.get('pressure', 0) <= 1100):
            return False
        
        return True


class SensorReader:
    """Main sensor reader class that handles all sensor types"""
    
    def __init__(self, sensor_type: str = "AUTO", **kwargs):
        """
        Initialize sensor reader
        
        Args:
            sensor_type: Type of sensor (AUTO, BME280, DHT22, SIMULATED)
            **kwargs: Additional arguments passed to specific sensor implementations
        """
        self.sensor_type = sensor_type.upper()
        self.sensor = None
        self.is_simulated = False
        
        # Auto-detect sensor type
        if self.sensor_type == "AUTO":
            if HARDWARE_AVAILABLE and not FORCE_SIMULATION:
                # Try BME280 first
                try:
                    self.sensor = BME280Sensor()
                    self.sensor_type = "BME280"
                    logger.info("Auto-detected BME280 sensor")
                except:
                    # Try DHT22
                    try:
                        self.sensor = DHT22Sensor()
                        self.sensor_type = "DHT22"
                        logger.info("Auto-detected DHT22 sensor")
                    except:
                        # Fall back to simulation
                        self.sensor = SimulatedSensor(**kwargs)
                        self.sensor_type = "SIMULATED"
                        self.is_simulated = True
                        logger.info("No hardware found, using simulation")
            else:
                # Use simulation
                self.sensor = SimulatedSensor(**kwargs)
                self.sensor_type = "SIMULATED"
                self.is_simulated = True
                logger.info("Using simulated sensor")
        
        # Specific sensor types
        elif self.sensor_type == "BME280":
            if HARDWARE_AVAILABLE:
                self.sensor = BME280Sensor()
            else:
                raise RuntimeError("BME280 hardware not available. Set SENSOR_TYPE=SIMULATED or install on Raspberry Pi.")
        
        elif self.sensor_type == "DHT22":
            if HARDWARE_AVAILABLE:
                self.sensor = DHT22Sensor(**kwargs)
            else:
                raise RuntimeError("DHT22 hardware not available. Set SENSOR_TYPE=SIMULATED or install on Raspberry Pi.")
        
        elif self.sensor_type == "SIMULATED":
            self.sensor = SimulatedSensor(**kwargs)
            self.is_simulated = True
        
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")
    
    def read_sensor(self) -> Optional[Dict[str, float]]:
        """
        Read data from the sensor
        
        Returns:
            Dictionary with sensor data or None if read fails
        """
        try:
            data = self.sensor.read()
            
            if data and self.sensor.validate_reading(data):
                return data
            else:
                logger.warning("Invalid sensor reading")
                return None
        except Exception as e:
            logger.error(f"Error reading sensor: {e}")
            return None
    
    def cleanup(self):
        """Clean up sensor resources"""
        if self.sensor:
            self.sensor.cleanup()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


# Convenience function for quick sensor access
def get_sensor(sensor_type: str = "AUTO", **kwargs) -> SensorReader:
    """
    Get a sensor reader instance
    
    Args:
        sensor_type: Type of sensor (AUTO, BME280, DHT22, SIMULATED)
        **kwargs: Additional arguments for sensor configuration
    
    Returns:
        SensorReader instance
    """
    return SensorReader(sensor_type=sensor_type, **kwargs)