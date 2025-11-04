from datetime import datetime, date
from flask import render_template, request, url_for, current_app, jsonify
from app import db
import sqlalchemy as sa
from app.sensor import bp
from app.models import Bme280Rpi, Bme280Outer, Dht22, BmeHistory
from app.utils.sensor_data import bme_rpi_table, bme_outer_table, dht_outer_table, history_table
from flask_babel import format_datetime

from app.sensor.sensor_rpi import BME280Module
bme = BME280Module()


@bp.app_template_filter('datetimeformat')
def datetimeformat(value):
    return format_datetime(value, 'd.MM.YY, HH:mm')
    # return datetime.strftime(value, '%d.%m.%y - %H:%M:%S')


@bp.app_template_filter('dateformat')
def dateformat(value):
    return format_datetime(value, 'd.MM.yyyy')
    # return datetime.strftime(value, '%d.%m.%y')


@bp.app_template_filter('time')
def timeformat(value):
    if value: 
        return format_datetime(value, 'HH:mm')
    else:
        return '-'


@bp.route('/sensors')
def sensors():
    return render_template('sensor/sensors_data.html', title='Sensors')


@bp.route('/api/table/bme280_rpi')
def bme280_rpi():
    """Return BME280 RPI data from db with pagination - for table"""
    page = request.args.get('page', 1, type=int)
    query = sa.select(Bme280Rpi).order_by(Bme280Rpi.created_at.desc())
    data = db.paginate(query, page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    next_url = url_for('sensor.api.table.bme280_rpi', page=data.next_num) \
        if data.has_next else None
    prev_url = url_for('sensor.api.table.bme280_rpi', page=data.prev_num) \
        if data.has_prev else None
    return render_template('sensor/sensor_table.html', title='BME280 RPI', data=data.items, next_url=next_url, prev_url=prev_url, table=bme_rpi_table)


@bp.route('/api/table/bme280_outer')
def bme280_outer():
    """Return BME280 Outer data from db with pagination - for table"""
    page = request.args.get('page', 1, type=int)
    query = sa.select(Bme280Outer).order_by(Bme280Outer.created_at.desc())
    data = db.paginate(query, page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    next_url = url_for('sensor.bme280_outer', page=data.next_num) \
        if data.has_next else None
    prev_url = url_for('sensor.bme280_outer', page=data.prev_num) \
        if data.has_prev else None
    return render_template('sensor/sensor_table.html', title='BME280 внешний', data=data.items, next_url=next_url, prev_url=prev_url, table=bme_outer_table)


@bp.route('/api/table/dht22_outer')
def dht22_outer():
    """Return DHT22 data from db with pagination - for table"""
    page = request.args.get('page', 1, type=int)
    query = sa.select(Dht22).order_by(Dht22.created_at.desc())
    data = db.paginate(query, page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    next_url = url_for('sensor.dht22_outer', page=data.next_num) \
        if data.has_next else None
    prev_url = url_for('sensor.dht22_outer', page=data.prev_num) \
        if data.has_prev else None
    return render_template('sensor/sensor_table.html', title='DHT22', data=data.items, next_url=next_url, prev_url=prev_url, table=dht_outer_table)


@bp.route('/api/table/bme_history')
def bme_history():
    """Return BME History data with pagination - for table"""
    page = request.args.get('page', 1, type=int)
    query = sa.select(BmeHistory).order_by(BmeHistory.date.desc())
    data = db.paginate(query, page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)   
    # data = db.session.scalars(query)
    next_url = url_for('sensor.bme_history', page=data.next_num) \
        if data.has_next else None
    prev_url = url_for('sensor.bme_history', page=data.prev_num) \
        if data.has_prev else None
    return render_template('sensor/sensor_table.html', title='BME280 история', data=data.items, next_url=next_url, prev_url=prev_url, table=history_table)


@bp.route('/api/json_history', methods=['GET', 'POST'])
def json_history():
    """Return BME History data for a specified time range"""
    start = request.args.get('start')
    end = request.args.get('end')
    print(f'params: {start} and {end}')

    if start and end:
        print('start', date.fromisoformat(start))
        print('end', date.fromisoformat(end))
        query = sa.select(BmeHistory).filter(BmeHistory.date >= date.fromisoformat(start), BmeHistory.date <= date.fromisoformat(end)).order_by(BmeHistory.date.desc())
    else:
        query = sa.select(BmeHistory).order_by(BmeHistory.date.desc()).limit(current_app.config['HISTORY_ITEMS_LIMIT'])
    data = db.session.scalars(query)

    if data:
        return [{
                'min_temperature': n.min_temperature,
                'max_temperature': n.max_temperature, 
                'min_humidity': n.min_humidity,
                'max_humidity': n.max_humidity, 
                'min_pressure': n.min_pressure, 
                'max_pressure': n.max_pressure, 
                'date': n.date,
            } for n in data]
    else:
        return {}


@bp.route('/api/bme280_rpi')
def get_sensor_readings():
    """Return the BME280 data when requested from the sensor"""
    temperature, pressure, humidity, created_at = bme.get_sensor_readings()
    return jsonify(
        {
            "status": "OK",
            "temperature": temperature,
            "pressure": pressure,
            "humidity": humidity,
            "created_at": created_at,
        }
    )


@bp.route('/api/bme280_db')
def get_bme280_latest_data():
    """Return the latest BME280 Outer data from db"""
    query = sa.select(Bme280Outer).order_by(Bme280Outer.created_at.desc())
    data = db.session.scalar(query)
    if data:
        return jsonify(
            {
                'temperature': data.temperature,
                'humidity': data.humidity,
                'pressure': data.pressure,
                'created_at': data.created_at,
            }
        )
    else:
        return jsonify(
            {
                'temperature': '-',
                'humidity': '-',
                'pressure': '-',
                'created_at': datetime.now(),
            }
        )



@bp.route('/api/bme280_mqtt')
def get_bme280_mqtt_data():
    """Return the latest BME280 data from MQTT callbacks"""
    latest_data = current_app.latest_bme280_data
    if latest_data:
        created_at = latest_data['created_at']
        return jsonify(
            {
                'temperature': latest_data['temperature'],
                'humidity': latest_data['humidity'],
                'pressure': latest_data['pressure'],
                'created_at': created_at.isoformat() if isinstance(created_at, datetime) else created_at,
            }
        )
    else:
        return jsonify(
            {
                'temperature': None,
                'humidity': None,
                'pressure': None,
                'created_at': None,
            }
        )


@bp.route('/api/dht22_db')
def get_dht22_latest_data():
    """Return the latest DHT22 data from db"""
    query = sa.select(Dht22).order_by(Dht22.created_at.desc())
    data = db.session.scalar(query)
    if data:
        return jsonify(
            {
                'temperature1': data.temperature1,
                'humidity1': data.humidity1,
                'temperature2': data.temperature2,
                'humidity2': data.humidity2,
                'created_at': data.created_at,
            }
        )
    else:
        return jsonify(
            {
                'temperature1': '-',
                'humidity1': '-',
                'temperature2': '-',
                'humidity2': '-',
                'created_at': datetime.now(),
            }
        )


@bp.route('/api/dht22_mqtt')
def get_dht22_mqtt_data():
    """Return the latest DHT22 data from MQTT callbacks"""
    latest_data = current_app.latest_dht22_data
    if latest_data:
        created_at = latest_data['created_at']
        return jsonify(
            {
                'temperature1': latest_data['temperature1'],
                'humidity1': latest_data['humidity1'],
                'temperature2': latest_data['temperature2'],
                'humidity2': latest_data['humidity2'],
                'created_at': created_at.isoformat() if isinstance(created_at, datetime) else created_at,
            }
        )
    else:
        return jsonify(
            {
                'temperature1': None,
                'humidity1': None,
                'temperature2': None,
                'humidity2': None,
                'created_at': None,
            }
        )
