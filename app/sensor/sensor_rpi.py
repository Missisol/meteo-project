import smbus2
import bme280
from app import db
from app.models import Bme280Rpi


class BME280Module:
    PORT = 1
    ADDRESS = 0x76

    def __init__(self):
      self.bus = smbus2.SMBus(BME280Module.PORT)
      self.calibration_params = bme280.load_calibration_params(self.bus, BME280Module.ADDRESS)

    def get_sensor_readings(self):
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
    
    
    def save_sensor_readings(self):
        temperature_val, pressure_val, humidity_val, timestamp_raw_val = self.get_sensor_readings()
        data = Bme280Rpi(temperature=temperature_val, humidity=humidity_val, pressure=pressure_val, created_at=timestamp_raw_val)

        db.session.add(data)
        db.session.commit()

