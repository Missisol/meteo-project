from flask import Blueprint

bp = Blueprint('cli', __name__, cli_group=None)

from app.sensor.sensor_rpi import BME280Module
bme = BME280Module()
from app.models import Bme280Rpi, Dht22
from app.sensor.sensor_history import get_minmax_bme_data, clear_db


@bp.cli.group()
def scheduled():
    """Cron job"""
    pass


@scheduled.command()
def bme280_rpi():
    """Save BME280-RPI data"""
    bme.save_sensor_readings()


@scheduled.command()
def minmax():
    """Get BME280-outer min-max data"""
    get_minmax_bme_data()


@scheduled.command()
def cleardb():
    """Clear BME280-RPI and DHT22 data"""
    clear_db(Bme280Rpi)
    clear_db(Dht22)