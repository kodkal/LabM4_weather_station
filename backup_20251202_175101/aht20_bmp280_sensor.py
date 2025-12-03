"""
AHT20 + BMP280 Combo Sensor Module
Compatible with the Weather Station IoT Security Lab

This module supports the AHT20+BMP280 combo board (like SimpleRobot)
which provides temperature, humidity, and pressure readings.

AHT20: Temperature + Humidity (I2C address 0x38)
BMP280: Temperature + Pressure (I2C address 0x76 or 0x77)

Note: Some combo boards only have the AHT20 working. This module
handles that gracefully and will still provide temp/humidity data.
"""

import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# I2C Addresses
ADDR_AHT20 = 0x38
BMP280_ADDRESSES = [0x76, 0x77]


class AHT20:
    """AHT20 Temperature and Humidity Sensor"""
    
    def __init__(self, bus):
        self.bus = bus
        self.addr = ADDR_AHT20
        self._soft_reset()
        self._init_sensor()
        logger.info(f"AHT20 initialized at 0x{self.addr:02X}")
    
    def _soft_reset(self):
        """Perform soft reset"""
        try:
            self.bus.write_byte(self.addr, 0xBA)
            time.sleep(0.02)
        except Exception as e:
            logger.error(f"AHT20 soft reset failed: {e}")
            raise
    
    def _init_sensor(self):
        """Initialize AHT20 sensor"""
        try:
            self.bus.write_i2c_block_data(self.addr, 0xBE, [0x08, 0x00])
            time.sleep(0.01)
        except Exception as e:
            logger.error(f"AHT20 init failed: {e}")
            raise
    
    def read(self) -> Optional[Dict[str, float]]:
        """Read temperature and humidity from AHT20"""
        try:
            # Trigger measurement
            self.bus.write_i2c_block_data(self.addr, 0xAC, [0x33, 0x00])
            time.sleep(0.08)
            
            # Read 7 bytes of data
            data = self.bus.read_i2c_block_data(self.addr, 0x00, 7)
            
            # Parse raw data
            raw_hum = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
            raw_temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
            
            # Convert to actual values
            humidity = raw_hum * 100.0 / (1 << 20)
            temp_c = raw_temp * 200.0 / (1 << 20) - 50.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            
            return {
                'temperature': round(temp_c, 2),
                'temperature_f': round(temp_f, 2),
                'humidity': round(humidity, 2)
            }
        except Exception as e:
            logger.error(f"AHT20 read failed: {e}")
            return None


class BMP280:
    """BMP280 Temperature and Pressure Sensor"""
    
    def __init__(self, bus):
        self.bus = bus
        self.addr = None
        
        # Auto-detect address
        for address in BMP280_ADDRESSES:
            try:
                chip_id = self.bus.read_byte_data(address, 0xD0)
                if chip_id == 0x58:  # BMP280 chip ID
                    self.addr = address
                    break
                elif chip_id == 0x60:  # BME280 chip ID (compatible)
                    self.addr = address
                    logger.info(f"Found BME280 (compatible) at 0x{address:02X}")
                    break
            except OSError:
                continue
        
        if self.addr is None:
            raise RuntimeError("BMP280 not found on 0x76 or 0x77")
        
        self._load_calibration()
        
        # Configure sensor: normal mode, 16x oversampling
        self.bus.write_byte_data(self.addr, 0xF4, 0x2F)
        self.bus.write_byte_data(self.addr, 0xF5, 0x00)
        
        logger.info(f"BMP280 initialized at 0x{self.addr:02X}")
    
    def _read_u16(self, reg):
        """Read unsigned 16-bit value"""
        lsb = self.bus.read_byte_data(self.addr, reg)
        msb = self.bus.read_byte_data(self.addr, reg + 1)
        return (msb << 8) | lsb
    
    def _read_s16(self, reg):
        """Read signed 16-bit value"""
        result = self._read_u16(reg)
        if result > 32767:
            result -= 65536
        return result
    
    def _load_calibration(self):
        """Load factory calibration data"""
        self.dig_T1 = self._read_u16(0x88)
        self.dig_T2 = self._read_s16(0x8A)
        self.dig_T3 = self._read_s16(0x8C)
        
        self.dig_P1 = self._read_u16(0x8E)
        self.dig_P2 = self._read_s16(0x90)
        self.dig_P3 = self._read_s16(0x92)
        self.dig_P4 = self._read_s16(0x94)
        self.dig_P5 = self._read_s16(0x96)
        self.dig_P6 = self._read_s16(0x98)
        self.dig_P7 = self._read_s16(0x9A)
        self.dig_P8 = self._read_s16(0x9C)
        self.dig_P9 = self._read_s16(0x9E)
    
    def _read_raw_data(self):
        """Read raw ADC values"""
        data = self.bus.read_i2c_block_data(self.addr, 0xF7, 6)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        return adc_t, adc_p
    
    def _compensate_temperature(self, adc_t):
        """Apply temperature compensation"""
        var1 = (adc_t / 16384.0 - self.dig_T1 / 1024.0) * self.dig_T2
        var2 = ((adc_t / 131072.0 - self.dig_T1 / 8192.0) ** 2) * self.dig_T3
        t_fine = var1 + var2
        temperature = t_fine / 5120.0
        return temperature, t_fine
    
    def _compensate_pressure(self, adc_p, t_fine):
        """Apply pressure compensation"""
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 += var1 * self.dig_P5 * 2
        var2 = var2 / 4.0 + self.dig_P4 * 65536.0
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        
        if var1 == 0:
            return 0
        
        pressure = 1048576.0 - adc_p
        pressure = (pressure - var2 / 4096.0) * 6250.0 / var1
        var1 = self.dig_P9 * pressure * pressure / 2147483648.0
        var2 = pressure * self.dig_P8 / 32768.0
        pressure += (var1 + var2 + self.dig_P7) / 16.0
        
        return pressure / 100.0  # Convert to hPa
    
    def read(self) -> Optional[Dict[str, float]]:
        """Read temperature and pressure from BMP280"""
        try:
            adc_t, adc_p = self._read_raw_data()
            temp_c, t_fine = self._compensate_temperature(adc_t)
            pressure = self._compensate_pressure(adc_p, t_fine)
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            
            # Calculate altitude from pressure (assuming sea level = 1013.25 hPa)
            altitude = 44330.0 * (1.0 - (pressure / 1013.25) ** 0.1903)
            
            return {
                'temperature': round(temp_c, 2),
                'temperature_f': round(temp_f, 2),
                'pressure': round(pressure, 2),
                'altitude': round(altitude, 2)
            }
        except Exception as e:
            logger.error(f"BMP280 read failed: {e}")
            return None


class AHT20BMP280Sensor:
    """
    Combined AHT20 + BMP280 Sensor Interface
    
    Compatible with the Weather Station Lab's SensorInterface
    Provides temperature, humidity, and pressure readings.
    
    Note: Works even if only AHT20 is available (no pressure data).
    """
    
    def __init__(self, bus=None):
        """
        Initialize the combo sensor
        
        Args:
            bus: SMBus instance (if None, will create one for bus 1)
        """
        if bus is None:
            from smbus import SMBus
            self.bus = SMBus(1)
            self._owns_bus = True
        else:
            self.bus = bus
            self._owns_bus = False
        
        self.aht20 = None
        self.bmp280 = None
        
        # Initialize AHT20
        try:
            self.aht20 = AHT20(self.bus)
            print(f"✓ AHT20 initialized at 0x{ADDR_AHT20:02X}")
        except Exception as e:
            print(f"✗ AHT20 initialization failed: {e}")
            logger.warning(f"AHT20 initialization failed: {e}")
        
        # Initialize BMP280
        try:
            self.bmp280 = BMP280(self.bus)
            print(f"✓ BMP280 initialized at 0x{self.bmp280.addr:02X}")
        except Exception as e:
            print(f"✗ BMP280 initialization failed: {e}")
            print("  (Pressure readings will not be available)")
            logger.warning(f"BMP280 initialization failed: {e}")
        
        if not self.aht20 and not self.bmp280:
            raise RuntimeError("Neither AHT20 nor BMP280 sensors found!")
        
        print()
        logger.info("AHT20+BMP280 combo sensor initialized")
    
    def read(self) -> Optional[Dict[str, float]]:
        """
        Read all sensor data
        
        Returns combined data from AHT20 (humidity) and BMP280 (pressure)
        Temperature is averaged from both sensors if both available
        """
        data = {}
        temps = []
        
        # Read AHT20 (temperature + humidity)
        if self.aht20:
            aht_data = self.aht20.read()
            if aht_data:
                data['humidity'] = aht_data['humidity']
                temps.append(aht_data['temperature'])
        
        # Read BMP280 (temperature + pressure)
        if self.bmp280:
            bmp_data = self.bmp280.read()
            if bmp_data:
                data['pressure'] = bmp_data['pressure']
                data['altitude'] = bmp_data['altitude']
                temps.append(bmp_data['temperature'])
        
        # Average temperatures if we have both, or use single reading
        if temps:
            avg_temp = sum(temps) / len(temps)
            data['temperature'] = round(avg_temp, 2)
            data['temperature_f'] = round(avg_temp * 9.0 / 5.0 + 32.0, 2)
        
        if not data:
            return None
        
        return data
    
    def validate_reading(self, data: Dict[str, float]) -> bool:
        """Validate sensor reading ranges"""
        if not data:
            return False
        
        # Temperature: -40°C to 85°C
        if 'temperature' in data:
            if not -40 <= data['temperature'] <= 85:
                return False
        
        # Humidity: 0% to 100%
        if 'humidity' in data:
            if not 0 <= data['humidity'] <= 100:
                return False
        
        # Pressure: 300 hPa to 1100 hPa
        if 'pressure' in data:
            if not 300 <= data['pressure'] <= 1100:
                return False
        
        return True
    
    def cleanup(self):
        """Clean up resources"""
        if self._owns_bus:
            try:
                self.bus.close()
            except:
                pass
    
    def get_status(self) -> Dict[str, bool]:
        """Return status of each sensor"""
        return {
            'aht20': self.aht20 is not None,
            'bmp280': self.bmp280 is not None,
            'has_temperature': self.aht20 is not None or self.bmp280 is not None,
            'has_humidity': self.aht20 is not None,
            'has_pressure': self.bmp280 is not None
        }


# ============================================================
# Integration with Weather Station Lab's SensorReader
# ============================================================

def patch_sensor_module():
    """
    Patch the lab's sensor_module.py to support AHT20+BMP280
    
    Call this before initializing SensorReader to add support
    for the AHT20+BMP280 combo sensor.
    """
    try:
        import sensor_module
        
        # Add AHT20BMP280 as a valid sensor type
        sensor_module.AHT20BMP280Sensor = AHT20BMP280Sensor
        
        # Store original __init__
        original_init = sensor_module.SensorReader.__init__
        
        def patched_init(self, sensor_type="AUTO", gpio_pin=4, simulation_config=None):
            if sensor_type.upper() == "AHT20BMP280":
                self.sensor_type = "AHT20BMP280"
                self.sensor = AHT20BMP280Sensor()
                self.is_simulated = False
                self.reading_history = []
                self.max_history_size = 10
                self.calibration = {
                    'temperature_offset': 0.0,
                    'humidity_offset': 0.0,
                    'pressure_offset': 0.0
                }
                self.total_reads = 0
                self.failed_reads = 0
                from datetime import datetime
                self.start_time = datetime.utcnow()
                logger.info("Sensor reader initialized with AHT20BMP280")
            else:
                original_init(self, sensor_type, gpio_pin, simulation_config)
        
        sensor_module.SensorReader.__init__ = patched_init
        logger.info("Patched sensor_module to support AHT20+BMP280")
        return True
        
    except ImportError:
        logger.warning("sensor_module not found - patch not applied")
        return False


# ============================================================
# Standalone Test
# ============================================================

def main():
    """Test the AHT20+BMP280 sensor"""
    import sys
    
    print("=" * 50)
    print("AHT20 + BMP280 Combo Sensor Test")
    print("=" * 50)
    print()
    
    try:
        sensor = AHT20BMP280Sensor()
        
        # Show sensor status
        status = sensor.get_status()
        print("Sensor Status:")
        print(f"  AHT20 (temp/humidity): {'✓ Available' if status['aht20'] else '✗ Not found'}")
        print(f"  BMP280 (pressure):     {'✓ Available' if status['bmp280'] else '✗ Not found'}")
        print()
        print("Starting readings (Ctrl+C to stop)...")
        print()
        
        while True:
            data = sensor.read()
            
            if data:
                # Build output line with available data
                parts = []
                
                if 'temperature' in data:
                    parts.append(f"Temp: {data['temperature']:.2f}°C ({data['temperature_f']:.2f}°F)")
                
                if 'humidity' in data:
                    parts.append(f"Humidity: {data['humidity']:.1f}%")
                
                if 'pressure' in data:
                    parts.append(f"Pressure: {data['pressure']:.2f} hPa")
                
                if 'altitude' in data:
                    parts.append(f"Alt: {data['altitude']:.1f}m")
                
                print("  " + "  |  ".join(parts))
            else:
                print("  Failed to read sensor data")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'sensor' in locals():
            sensor.cleanup()
            print("Sensor cleanup complete.")


if __name__ == "__main__":
    main()