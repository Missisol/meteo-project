from flask import Blueprint
import click

bp = Blueprint('cli', __name__, cli_group=None)

from app.sensor.sensor_rpi import BME280Module
bme = BME280Module()
from app.models import Bme280Rpi, Dht22
from app.sensor.sensor_history import get_minmax_bme_data, clear_db, delete_history_data


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
    

@scheduled.command()
@click.option('--days', default=10, help='Number of days to delete history data for')
def delete_history(days):
    """Delete BmeHistory data for a date
    Command example:
    flask scheduled delete-history --days 4
    """
    delete_history_data(days)
