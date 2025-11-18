"""
Sensor Module for Weather Station
Interfaces with temperature, humidity, and pressure sensors
Includes comprehensive simulation mode for testing without hardware
"""

import os
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

# Try to import hardware libraries (will fail in development environments)
try:
    if not FORCE_SIMULATION:
        import board
        import adafruit_bme280.advanced as adafruit_bme280
        import adafruit_dht
        import RPi.GPIO as GPIO
        HARDWARE_AVAILABLE = True
    else:
        logger.info("Simulation mode forced via SENSOR_SIMULATION environment variable")
        HARDWARE_AVAILABLE = False
except ImportError:
    logger.warning("Hardware libraries not available - using simulation mode")
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
        self.address = i2c_address
        self.sensor = None
        
        if HARDWARE_AVAILABLE:
            try:
                import busio
                i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=i2c_address)
                
                # Configure sensor for weather monitoring
                self.sensor.mode = adafruit_bme280.MODE_NORMAL
                self.sensor.standby_period = adafruit_bme280.STANDBY_TC_500
                self.sensor.iir_filter = adafruit_bme280.IIR_FILTER_X16
                self.sensor.overscan_pressure = adafruit_bme280.OVERSCAN_X16
                self.sensor.overscan_humidity = adafruit_bme280.OVERSCAN_X1
                self.sensor.overscan_temperature = adafruit_bme280.OVERSCAN_X2
                
                # Set sea level pressure for altitude calculation
                self.sensor.sea_level_pressure = 1013.25
                
                logger.info(f"BME280 sensor initialized at address 0x{i2c_address:02x}")
            except Exception as e:
                logger.error(f"Failed to initialize BME280: {e}")
                self.sensor = None
        else:
            logger.info("BME280 running in simulation mode")
    
    def read(self) -> Dict[str, float]:
        """Read temperature, humidity, and pressure"""
        try:
            if self.sensor:
                # Read from actual sensor
                data = {
                    'temperature': round(self.sensor.temperature, 2),
                    'humidity': round(self.sensor.relative_humidity, 2),
                    'pressure': round(self.sensor.pressure, 2),
                    'altitude': round(self.sensor.altitude, 2)
                }
            else:
                # Simulation mode
                data = self._simulate_reading()
            
            # Validate reading
            if self.validate_reading(data):
                return data
            else:
                logger.warning("Invalid sensor reading detected")
                return None
                
        except Exception as e:
            logger.error(f"Error reading BME280: {e}")
            return None
    
    def _simulate_reading(self) -> Dict[str, float]:
        """Generate simulated sensor data for testing"""
        base_temp = 22.0
        base_humidity = 50.0
        base_pressure = 1013.25
        
        # Add realistic variations
        temp_variation = random.gauss(0, 2)
        humidity_variation = random.gauss(0, 5)
        pressure_variation = random.gauss(0, 5)
        
        return {
            'temperature': round(base_temp + temp_variation, 2),
            'humidity': round(max(0, min(100, base_humidity + humidity_variation)), 2),
            'pressure': round(base_pressure + pressure_variation, 2),
            'altitude': round(44330.0 * (1.0 - ((base_pressure + pressure_variation) / 1013.25) ** 0.1903), 2)
        }
    
    def validate_reading(self, data: Dict[str, float]) -> bool:
        """Validate sensor reading is within reasonable bounds"""
        if not data:
            return False
        
        # Temperature: -40°C to 85°C (sensor range)
        if not -40 <= data.get('temperature', -100) <= 85:
            return False
        
        # Humidity: 0% to 100%
        if not 0 <= data.get('humidity', -1) <= 100:
            return False
        
        # Pressure: 300 hPa to 1100 hPa
        if not 300 <= data.get('pressure', 0) <= 1100:
            return False
        
        # Altitude: -500m to 9000m
        if not -500 <= data.get('altitude', -1000) <= 9000:
            return False
        
        return True
    
    def cleanup(self):
        """Clean up sensor resources"""
        # BME280 doesn't require explicit cleanup
        pass


class DHT22Sensor(SensorInterface):
    """DHT22 Temperature and Humidity Sensor"""
    
    def __init__(self, gpio_pin: int = 4):
        """Initialize DHT22 sensor"""
        self.gpio_pin = gpio_pin
        self.sensor = None
        
        if HARDWARE_AVAILABLE:
            try:
                # Map GPIO pin to board pin
                pin_mapping = {
                    4: board.D4,
                    17: board.D17,
                    27: board.D27,
                    22: board.D22
                }
                
                board_pin = pin_mapping.get(gpio_pin, board.D4)
                self.sensor = adafruit_dht.DHT22(board_pin)
                
                logger.info(f"DHT22 sensor initialized on GPIO pin {gpio_pin}")
            except Exception as e:
                logger.error(f"Failed to initialize DHT22: {e}")
                self.sensor = None
        else:
            logger.info("DHT22 running in simulation mode")
    
    def read(self) -> Dict[str, float]:
        """Read temperature and humidity"""
        try:
            if self.sensor:
                # DHT22 can be unreliable, retry a few times
                for attempt in range(3):
                    try:
                        temperature = self.sensor.temperature
                        humidity = self.sensor.humidity
                        
                        if temperature is not None and humidity is not None:
                            data = {
                                'temperature': round(temperature, 2),
                                'humidity': round(humidity, 2)
                            }
                            
                            if self.validate_reading(data):
                                return data
                            
                    except RuntimeError as e:
                        logger.debug(f"DHT22 read attempt {attempt + 1} failed: {e}")
                        time.sleep(2)
                
                logger.warning("Failed to read DHT22 after 3 attempts")
                return None
            else:
                # Simulation mode
                return self._simulate_reading()
                
        except Exception as e:
            logger.error(f"Error reading DHT22: {e}")
            return None
    
    def _simulate_reading(self) -> Dict[str, float]:
        """Generate simulated sensor data"""
        return {
            'temperature': round(20.0 + random.gauss(0, 3), 2),
            'humidity': round(max(0, min(100, 60.0 + random.gauss(0, 10))), 2)
        }
    
    def validate_reading(self, data: Dict[str, float]) -> bool:
        """Validate sensor reading"""
        if not data:
            return False
        
        # Temperature: -40°C to 80°C (DHT22 range)
        if not -40 <= data.get('temperature', -100) <= 80:
            return False
        
        # Humidity: 0% to 100%
        if not 0 <= data.get('humidity', -1) <= 100:
            return False
        
        return True
    
    def cleanup(self):
        """Clean up sensor resources"""
        if self.sensor:
            try:
                self.sensor.exit()
            except:
                pass


class SensorReader:
    """
    Main sensor reader that manages different sensor types
    Automatically falls back to simulation if hardware is unavailable
    """
    
    def __init__(self, sensor_type: str = "AUTO", 
                 gpio_pin: int = 4,
                 simulation_config: Dict = None):
        """
        Initialize sensor reader
        
        Args:
            sensor_type: Type of sensor (BME280, DHT22, SIMULATED, AUTO)
            gpio_pin: GPIO pin for DHT22 sensor
            simulation_config: Configuration for simulation mode
        """
        self.sensor_type = sensor_type.upper()
        self.sensor = None
        self.is_simulated = False
        
        # Simulation configuration
        sim_config = simulation_config or {}
        
        # AUTO mode: try hardware first, fall back to simulation
        if self.sensor_type == "AUTO":
            if HARDWARE_AVAILABLE:
                # Try to detect which sensor is connected
                try:
                    self.sensor = BME280Sensor()
                    test_read = self.sensor.read()
                    if test_read:
                        self.sensor_type = "BME280"
                        logger.info("Auto-detected BME280 sensor")
                    else:
                        raise Exception("BME280 not responding")
                except:
                    try:
                        self.sensor = DHT22Sensor(gpio_pin)
                        test_read = self.sensor.read()
                        if test_read:
                            self.sensor_type = "DHT22"
                            logger.info("Auto-detected DHT22 sensor")
                        else:
                            raise Exception("DHT22 not responding")
                    except:
                        logger.warning("No hardware sensors detected, using simulation")
                        self.sensor_type = "SIMULATED"
            else:
                logger.info("Hardware not available, using simulation")
                self.sensor_type = "SIMULATED"
        
        # Initialize appropriate sensor based on type
        if self.sensor_type == "SIMULATED" or FORCE_SIMULATION:
            self.sensor = SimulatedSensor(
                pattern=sim_config.get('pattern'),
                enable_anomalies=sim_config.get('enable_anomalies', False),
                location=sim_config.get('location', 'utah')
            )
            self.is_simulated = True
            logger.info("Using simulated sensor")
        elif self.sensor_type == "BME280" and not self.sensor:
            if HARDWARE_AVAILABLE:
                self.sensor = BME280Sensor()
            else:
                logger.warning("BME280 requested but hardware unavailable, using simulation")
                self.sensor = SimulatedSensor(location='utah')
                self.is_simulated = True
        elif self.sensor_type == "DHT22" and not self.sensor:
            if HARDWARE_AVAILABLE:
                self.sensor = DHT22Sensor(gpio_pin)
            else:
                logger.warning("DHT22 requested but hardware unavailable, using simulation")
                self.sensor = SimulatedSensor(location='utah')
                self.is_simulated = True
        
        # Ensure we have a sensor
        if not self.sensor:
            logger.warning(f"Unknown sensor type: {sensor_type}, using simulation")
            self.sensor = SimulatedSensor()
            self.is_simulated = True
        
        # Track reading history for anomaly detection
        self.reading_history = []
        self.max_history_size = 10
        
        # Calibration offsets
        self.calibration = {
            'temperature_offset': 0.0,
            'humidity_offset': 0.0,
            'pressure_offset': 0.0
        }
        
        # Statistics tracking
        self.total_reads = 0
        self.failed_reads = 0
        self.start_time = datetime.utcnow()
        
        logger.info(f"Sensor reader initialized with {self.sensor_type}" + 
                   (" (SIMULATED)" if self.is_simulated else ""))
    
    def read_sensor(self) -> Optional[Dict[str, float]]:
        """Read data from sensor with error handling"""
        try:
            self.total_reads += 1
            
            # Read raw data
            raw_data = self.sensor.read()
            
            if raw_data is None:
                self.failed_reads += 1
                logger.warning(f"Sensor read failed (attempt {self.total_reads}, " +
                             f"failure rate: {self.failed_reads/self.total_reads:.1%})")
                return None
            
            # Apply calibration
            calibrated_data = self._apply_calibration(raw_data)
            
            # Check for anomalies (unless it's simulated data with anomalies enabled)
            if not (self.is_simulated and calibrated_data.get('weather_pattern')):
                if self._detect_anomaly(calibrated_data):
                    logger.warning("Anomaly detected in sensor reading")
                    calibrated_data['anomaly_detected'] = True
            
            # Update history
            self._update_history(calibrated_data)
            
            # Add metadata
            calibrated_data['timestamp'] = datetime.utcnow().isoformat()
            calibrated_data['sensor_type'] = self.sensor_type
            calibrated_data['is_simulated'] = self.is_simulated
            
            # Add read statistics
            calibrated_data['read_number'] = self.total_reads
            calibrated_data['failure_rate'] = round(
                (self.failed_reads / self.total_reads) * 100, 2
            ) if self.total_reads > 0 else 0
            
            return calibrated_data
            
        except Exception as e:
            self.failed_reads += 1
            logger.error(f"Error reading sensor: {e}")
            return None
    
    def _apply_calibration(self, data: Dict[str, float]) -> Dict[str, float]:
        """Apply calibration offsets to sensor data"""
        calibrated = data.copy()
        
        for key in ['temperature', 'humidity', 'pressure']:
            if key in calibrated and f'{key}_offset' in self.calibration:
                calibrated[key] += self.calibration[f'{key}_offset']
                calibrated[key] = round(calibrated[key], 2)
        
        return calibrated
    
    def _detect_anomaly(self, data: Dict[str, float]) -> bool:
        """Detect anomalies in sensor readings"""
        if len(self.reading_history) < 3:
            return False  # Not enough history
        
        # Check for sudden changes
        for key in ['temperature', 'humidity', 'pressure']:
            if key not in data:
                continue
            
            # Get recent values
            recent_values = [h.get(key) for h in self.reading_history[-3:] if key in h]
            
            if recent_values:
                avg_recent = sum(recent_values) / len(recent_values)
                current = data[key]
                
                # Define thresholds for sudden changes
                thresholds = {
                    'temperature': 5.0,  # 5°C change
                    'humidity': 20.0,    # 20% change
                    'pressure': 10.0     # 10 hPa change
                }
                
                if abs(current - avg_recent) > thresholds.get(key, float('inf')):
                    logger.warning(f"Anomaly detected: {key} changed from {avg_recent:.2f} to {current:.2f}")
                    return True
        
        return False
    
    def _update_history(self, data: Dict[str, float]):
        """Update reading history"""
        self.reading_history.append(data.copy())
        
        # Limit history size
        if len(self.reading_history) > self.max_history_size:
            self.reading_history.pop(0)
    
    def set_calibration(self, temperature_offset: float = 0.0, 
                       humidity_offset: float = 0.0,
                       pressure_offset: float = 0.0):
        """Set calibration offsets"""
        self.calibration = {
            'temperature_offset': temperature_offset,
            'humidity_offset': humidity_offset,
            'pressure_offset': pressure_offset
        }
        logger.info(f"Calibration set: {self.calibration}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from reading history"""
        if not self.reading_history:
            return {}
        
        stats = {}
        
        for key in ['temperature', 'humidity', 'pressure']:
            values = [h.get(key) for h in self.reading_history if key in h]
            
            if values:
                stats[key] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'current': values[-1] if values else None
                }
        
        stats['total_readings'] = len(self.reading_history)
        stats['sensor_type'] = self.sensor_type
        
        return stats
    
    def cleanup(self):
        """Clean up sensor resources"""
        if self.sensor:
            self.sensor.cleanup()
        logger.info("Sensor reader cleaned up")


class SimulatedSensor(SensorInterface):
    """
    Advanced simulated sensor for testing without hardware
    Provides realistic weather patterns and variations
    """
    
    def __init__(self, pattern: WeatherPattern = None, 
                 enable_anomalies: bool = False,
                 location: str = "default"):
        """
        Initialize simulated sensor with weather patterns
        
        Args:
            pattern: Specific weather pattern to simulate
            enable_anomalies: Whether to include random anomalies
            location: Location for realistic patterns (affects base values)
        """
        # Base values by location
        location_configs = {
            "default": {"temp": 22.0, "humidity": 50.0, "pressure": 1013.25},
            "utah": {"temp": 18.0, "humidity": 35.0, "pressure": 1020.0},
            "tropical": {"temp": 28.0, "humidity": 75.0, "pressure": 1012.0},
            "arctic": {"temp": -5.0, "humidity": 60.0, "pressure": 1015.0},
            "desert": {"temp": 32.0, "humidity": 20.0, "pressure": 1018.0}
        }
        
        config = location_configs.get(location.lower(), location_configs["default"])
        self.base_temperature = config["temp"]
        self.base_humidity = config["humidity"]
        self.base_pressure = config["pressure"]
        
        # Weather pattern
        self.pattern = pattern or random.choice(list(WeatherPattern))
        self.pattern_start_time = time.time()
        self.pattern_duration = random.randint(3600, 14400)  # 1-4 hours
        
        # Simulation parameters
        self.enable_anomalies = enable_anomalies
        self.time_factor = 0
        self.daily_cycle_position = random.uniform(0, 2 * math.pi)
        
        # Weather pattern effects
        self.pattern_effects = {
            WeatherPattern.SUNNY: {
                "temp_offset": 3.0,
                "humidity_offset": -10.0,
                "pressure_offset": 5.0,
                "variability": 0.5
            },
            WeatherPattern.CLOUDY: {
                "temp_offset": -1.0,
                "humidity_offset": 5.0,
                "pressure_offset": -2.0,
                "variability": 0.3
            },
            WeatherPattern.RAINY: {
                "temp_offset": -3.0,
                "humidity_offset": 25.0,
                "pressure_offset": -8.0,
                "variability": 1.0
            },
            WeatherPattern.STORMY: {
                "temp_offset": -5.0,
                "humidity_offset": 30.0,
                "pressure_offset": -15.0,
                "variability": 2.0
            },
            WeatherPattern.COLD_FRONT: {
                "temp_offset": -8.0,
                "humidity_offset": -5.0,
                "pressure_offset": 10.0,
                "variability": 1.5
            },
            WeatherPattern.HEAT_WAVE: {
                "temp_offset": 8.0,
                "humidity_offset": -15.0,
                "pressure_offset": -3.0,
                "variability": 0.8
            }
        }
        
        # Track historical data for realistic transitions
        self.history = []
        self.max_history = 10
        
        logger.info(f"Simulated sensor initialized with {self.pattern.value} pattern for {location}")
    
    def read(self) -> Dict[str, float]:
        """Generate realistic simulated weather reading"""
        try:
            # Check if pattern should change
            if time.time() - self.pattern_start_time > self.pattern_duration:
                self._transition_weather_pattern()
            
            # Get current pattern effects
            effects = self.pattern_effects[self.pattern]
            
            # Calculate daily cycle (temperature varies throughout the day)
            self.daily_cycle_position += 0.01  # Advance time
            daily_temp_variation = 4.0 * math.sin(self.daily_cycle_position)
            daily_humidity_variation = -2.0 * math.sin(self.daily_cycle_position + math.pi/4)
            
            # Generate base readings with pattern effects
            temperature = (
                self.base_temperature + 
                effects["temp_offset"] + 
                daily_temp_variation +
                random.gauss(0, effects["variability"])
            )
            
            humidity = (
                self.base_humidity + 
                effects["humidity_offset"] + 
                daily_humidity_variation +
                random.gauss(0, effects["variability"] * 2)
            )
            
            pressure = (
                self.base_pressure + 
                effects["pressure_offset"] +
                random.gauss(0, effects["variability"] * 0.5)
            )
            
            # Add smooth transitions from history
            if self.history:
                last_reading = self.history[-1]
                # Smooth transitions (max 2°C change per reading)
                temperature = self._smooth_transition(
                    temperature, last_reading.get('temperature', temperature), 2.0
                )
                humidity = self._smooth_transition(
                    humidity, last_reading.get('humidity', humidity), 5.0
                )
                pressure = self._smooth_transition(
                    pressure, last_reading.get('pressure', pressure), 2.0
                )
            
            # Apply constraints
            humidity = max(0, min(100, humidity))
            pressure = max(950, min(1050, pressure))
            
            # Add occasional anomalies if enabled
            if self.enable_anomalies and random.random() < 0.02:  # 2% chance
                anomaly_type = random.choice(['spike', 'drop', 'noise'])
                if anomaly_type == 'spike':
                    temperature += random.uniform(5, 10)
                    logger.debug("Simulating temperature spike anomaly")
                elif anomaly_type == 'drop':
                    temperature -= random.uniform(5, 10)
                    logger.debug("Simulating temperature drop anomaly")
                else:
                    # Add noise to all readings
                    temperature += random.gauss(0, 5)
                    humidity += random.gauss(0, 10)
                    pressure += random.gauss(0, 5)
                    logger.debug("Simulating sensor noise anomaly")
            
            # Calculate altitude based on pressure
            altitude = 44330.0 * (1.0 - (pressure / 1013.25) ** 0.1903)
            
            data = {
                'temperature': round(temperature, 2),
                'humidity': round(humidity, 2),
                'pressure': round(pressure, 2),
                'altitude': round(altitude, 2),
                'weather_pattern': self.pattern.value,  # For debugging
                'simulated': True  # Flag to indicate simulated data
            }
            
            # Update history
            self.history.append(data.copy())
            if len(self.history) > self.max_history:
                self.history.pop(0)
            
            # Validate reading
            if self.validate_reading(data):
                return data
            else:
                logger.warning("Invalid simulated reading generated, using defaults")
                return {
                    'temperature': 22.0,
                    'humidity': 50.0,
                    'pressure': 1013.25,
                    'altitude': 0.0,
                    'simulated': True
                }
                
        except Exception as e:
            logger.error(f"Error generating simulated data: {e}")
            return None
    
    def _transition_weather_pattern(self):
        """Transition to a new weather pattern realistically"""
        old_pattern = self.pattern
        
        # Define realistic transitions
        transitions = {
            WeatherPattern.SUNNY: [WeatherPattern.CLOUDY, WeatherPattern.HEAT_WAVE],
            WeatherPattern.CLOUDY: [WeatherPattern.SUNNY, WeatherPattern.RAINY],
            WeatherPattern.RAINY: [WeatherPattern.CLOUDY, WeatherPattern.STORMY],
            WeatherPattern.STORMY: [WeatherPattern.RAINY, WeatherPattern.CLOUDY],
            WeatherPattern.COLD_FRONT: [WeatherPattern.CLOUDY, WeatherPattern.SUNNY],
            WeatherPattern.HEAT_WAVE: [WeatherPattern.SUNNY, WeatherPattern.CLOUDY]
        }
        
        # Choose new pattern based on current pattern
        possible_patterns = transitions.get(self.pattern, list(WeatherPattern))
        self.pattern = random.choice(possible_patterns)
        
        # Reset pattern timer
        self.pattern_start_time = time.time()
        self.pattern_duration = random.randint(3600, 14400)
        
        logger.info(f"Weather pattern changed from {old_pattern.value} to {self.pattern.value}")
    
    def _smooth_transition(self, target: float, current: float, max_change: float) -> float:
        """Smooth transitions between readings"""
        change = target - current
        if abs(change) > max_change:
            change = max_change if change > 0 else -max_change
        return current + change
    
    def validate_reading(self, data: Dict[str, float]) -> bool:
        """Basic validation for simulated data"""
        if not data:
            return False
        
        # Temperature: -50°C to 60°C
        if not -50 <= data.get('temperature', -100) <= 60:
            return False
        
        # Humidity: 0% to 100%
        if not 0 <= data.get('humidity', -1) <= 100:
            return False
        
        # Pressure: 950 hPa to 1050 hPa (reasonable range for weather)
        if not 950 <= data.get('pressure', 0) <= 1050:
            return False
        
        return True
    
    def cleanup(self):
        """No cleanup needed for simulation"""
        logger.info("Simulated sensor cleanup (no action needed)")
    
    def set_weather_pattern(self, pattern: WeatherPattern):
        """Manually set weather pattern for testing"""
        self.pattern = pattern
        self.pattern_start_time = time.time()
        logger.info(f"Weather pattern manually set to {pattern.value}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get simulation status for debugging"""
        return {
            'current_pattern': self.pattern.value,
            'pattern_duration_remaining': max(0, 
                self.pattern_duration - (time.time() - self.pattern_start_time)),
            'base_values': {
                'temperature': self.base_temperature,
                'humidity': self.base_humidity,
                'pressure': self.base_pressure
            },
            'anomalies_enabled': self.enable_anomalies,
            'history_size': len(self.history)
        }