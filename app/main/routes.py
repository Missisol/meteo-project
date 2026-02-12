from datetime import datetime, date, timezone
from flask import render_template, request, url_for, jsonify
from flask_babel import format_datetime
import sqlalchemy as sa

from app import db
from app.main import bp
from app.models import Bme280Outer
from app.utils.sensor_data import list_bme, list_dht, sensors_list, weather_list
from app.utils.common_data import main_menu, theme_switcher, form_buttons


@bp.app_template_filter('datetimeformat')
def datetimeformat(value):
    return format_datetime(value, 'd.MM.YY, HH:mm')
    # return datetime.strftime(value, '%d.%m.%y, %H:%M')
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


@bp.route('/')
@bp.route('/home')
def index():
    return render_template('main/home.html', title='Home')


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
                'created_at': datetime.now(timezone.utc),
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