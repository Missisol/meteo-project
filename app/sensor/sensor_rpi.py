import smbus2
import bme280
from app import db
from app.models import Bme280Rpi
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class BME280Module:
    PORT = 1
    ADDRESS = 0x76

    def __init__(self):
        try:
            self.bus = smbus2.SMBus(BME280Module.PORT)
            self.calibration_params = bme280.load_calibration_params(self.bus, BME280Module.ADDRESS)
            self.sensor_available = True
        except Exception as e:
            logger.warning(f"Не удалось инициализировать датчик BME280: {e}. Будут возвращаться нулевые значения.")
            self.sensor_available = False
            self.bus = None
            self.calibration_params = None

    def get_sensor_readings(self):
        if not self.sensor_available:
            logger.warning("Датчик BME280 недоступен. Возвращаю нулевые значения.")
            return (0.0, 0, 0.0, datetime.now())
        
        try:
            sample_reading = bme280.sample(self.bus, BME280Module.ADDRESS, self.calibration_params)
            temperature_val = round(sample_reading.temperature, 1)
            humidity_val = round(sample_reading.humidity, 1)
            pressure_raw_val = sample_reading.pressure
            timestamp_raw_val = sample_reading.timestamp

            # Pressure convertion to mmHg
            pressure_val = round(pressure_raw_val * 0.75)

            # utc datetime convert to local datetime
            # timestamp_val = timestamp_raw_val.astimezone()

            print(f"temperature RPI: {temperature_val}")
            print(f'timestamp: {timestamp_raw_val}')
            return (temperature_val, pressure_val, humidity_val, timestamp_raw_val)
            
        except Exception as e:
            logger.warning(f"Ошибка при чтении данных с датчика BME280: {e}. Возвращаю нулевые значения.")
            return (0.0, 0, 0.0, datetime.now())
    
    
    def save_sensor_readings(self):
        try:
            temperature_val, pressure_val, humidity_val, timestamp_raw_val = self.get_sensor_readings()
            data = Bme280Rpi(temperature=temperature_val, humidity=humidity_val, pressure=pressure_val, created_at=timestamp_raw_val)

            db.session.add(data)
            db.session.commit()
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных датчика BME280: {e}")
            db.session.rollback()

