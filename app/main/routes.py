from datetime import datetime, date
from flask import render_template, request, url_for, jsonify
from app import db
import sqlalchemy as sa
from app.main import bp
from app.sensor.sensor_rpi import BME280Module
from app.models import Bme280Outer
from app.utils.sensor_data import list_bme, list_dht, sensors_list, weather_list, theme_switcher, form_buttons, main_menu

bme = BME280Module()


@bp.route('/')
@bp.route('/home')
def index():
    return render_template('home.html', title='Home')


@bp.route('/bme280Outer')
def get_bme_mqtt_data():
    query = sa.select(Bme280Outer).order_by(Bme280Outer.created_at.desc())
    data = db.session.scalar(query)
    if data:
        return jsonify(
            {
                'temperature': data.temperature,
                'humidity': data.humidity,
                'pressure': data.pressure,
                'created_at': data.created_at,
                'date': data.date,
            }
        )
    else:
        return jsonify(
            {
                'temperature': '-',
                'humidity': '-',
                'pressure': '-',
                'created_at': datetime.now(),
                'date': date.today(),
            }
        )


@bp.app_context_processor
def inject_data():
    return dict(
        {
            'bme_list': list_bme,
            'dht_list': list_dht,
            'sensors_list': sensors_list,
            'weather_list': weather_list,
            'theme_switcher': theme_switcher,
            'form_buttons': form_buttons,
            'menu': main_menu,
        }
    )