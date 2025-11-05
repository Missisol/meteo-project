import ast
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta, timezone
from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_babel import Babel

def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

def get_timezone():
    return current_app.config['TIMEZONE']


db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    babel.init_app(app, locale_selector=get_locale, timezone_selector=get_timezone)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.sensor import bp as sensor_bp
    app.register_blueprint(sensor_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)

    from app.pwa import bp as pwa_bp
    app.register_blueprint(pwa_bp)


    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/meteo.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Meteo startup')
        

    # Initialize sensor data storage and last save times
    app.latest_bme280_data = None
    app.latest_dht22_data = None
    app.last_bme280_save = None
    app.last_dht22_save = None

    def on_message_from_bme280(client, userdata, message):
        print(f"{message.topic} {message.payload}")
        if message.topic == app.config['MQTT_TOPIC_BME280']:
            print("BME readings update")
            socketio.emit('bme_message', message.payload.decode())

            data = ast.literal_eval(message.payload.decode())
            # if int(data['pressure']) > 0:
            temperature_val = float(data['temperature'])
            humidity_val = float(data['humidity'])
            pressure_val = round(int(data['pressure']))

            # Always update latest data
            app.latest_bme280_data = {
                'temperature': temperature_val,
                'humidity': humidity_val,
                'pressure': pressure_val,
                'created_at': datetime.now(timezone.utc)
            }

            # Save once per hour at the top of each hour (e.g., 1:00 PM, 2:00 PM, etc.)
            now = datetime.now()
            today = now.date()
            # Calculate the current hour slot (e.g., 1:00 PM if current time is 1:23 PM)
            current_hour_slot = datetime.combine(today, datetime.min.time()).replace(hour=now.hour)

            should_save = now >= current_hour_slot and (
                app.last_bme280_save is None or app.last_bme280_save < current_hour_slot
            )

            if should_save and temperature_val < 100 and humidity_val != 100 and pressure_val > 0 and pressure_val < 800:
                mod = models.Bme280Outer(temperature=temperature_val, humidity=humidity_val, pressure=pressure_val)
                save_on_db(mod)
                app.last_bme280_save = now
                print(f"BME280 data saved to DB at {now} for hour slot starting {current_hour_slot}")
            elif should_save:
                print('Sensor data error for saving')
            else:
                print(f"BME280 data received but not saved (last save: {app.last_bme280_save}, current hour slot: {current_hour_slot})")

            # Вариант с установкой произвольного интервала времени между сохранениями в базе
            # Only save to DB if some minutes have passed since last save
            # now = datetime.now()
            # should_save = False
            
            # if app.last_bme280_save is None:
            #     should_save = True
            # else:
            #     time_since_last_save = now - app.last_bme280_save
            #     if time_since_last_save >= timedelta(minutes=app.config['SAVE_INTERVAL']):
            #         should_save = True

            # if should_save and temperature_val < 100 and humidity_val != 100 and pressure_val > 0 and pressure_val < 800:
            #     mod = models.Bme280Outer(temperature=app.latest_bme280_data['temperature'], humidity=app.latest_bme280_data['humidity'], pressure=app.latest_bme280_data['pressure'], created_at=app.latest_bme280_data['created_at'])
            #     save_on_db(mod)
            #     app.last_bme280_save = now
            #     print(f"BME280 data saved to DB at {now}")
            # elif should_save:
            #     print('Sensor data error for saving')
            # else:
            #     print(f"BME280 data received but not saved (last save: {app.last_bme280_save})")


    def on_message_from_dht22(client, userdata, message):
        print(f"{message.topic} {message.payload}")
        if message.topic == app.config['MQTT_TOPIC_DHT22']:
            print("DHT readings update")
            socketio.emit('dht_message', message.payload.decode())

            data = ast.literal_eval(message.payload.decode())
            temperature_1 = float(data['temperature1'])
            humidity_1 = float(data['humidity1'])
            temperature_2 = float(data['temperature2'])
            humidity_2 = float(data['humidity2'])

            # Always update latest data
            app.latest_dht22_data = {
                'temperature1': temperature_1,
                'humidity1': humidity_1,
                'temperature2': temperature_2,
                'humidity2': humidity_2,
                'created_at': datetime.now(timezone.utc)
            }

            # Save only twice a day: at 03:00 and 15:00 (first message after those times)
            now = datetime.now()
            today = now.date()
            slot_morning = datetime.combine(today, datetime.min.time()).replace(hour=3)
            slot_evening = datetime.combine(today, datetime.min.time()).replace(hour=15)

            if now >= slot_evening:
                current_slot = slot_evening
            elif now >= slot_morning:
                current_slot = slot_morning
            else:
                current_slot = slot_morning  # upcoming slot; do not save until reached

            should_save = now >= current_slot and (
                app.last_dht22_save is None or app.last_dht22_save < current_slot
            )

            if should_save:
                mod = models.Dht22(temperature1=app.latest_dht22_data['temperature1'], humidity1=app.latest_dht22_data['humidity1'], temperature2=app.latest_dht22_data['temperature2'], humidity2=app.latest_dht22_data['humidity2'], created_at=app.latest_dht22_data['created_at'])
                save_on_db(mod)
                app.last_dht22_save = now
                print(f"DHT22 data saved to DB at {now} for slot starting {current_slot}")
            else:
                print(f"DHT22 data received but not saved (last save: {app.last_dht22_save}, current slot: {current_slot})")


    def save_on_db(data):
        with app.app_context():
            db.session.add(data)
            db.session.commit()


    mqttc = connect_mqtt()
    mqttc.message_callback_add(app.config['MQTT_TOPIC_BME280'], on_message_from_bme280)
    mqttc.message_callback_add(app.config['MQTT_TOPIC_DHT22'], on_message_from_dht22)

    return app

from app import models
from app.sensor.sensor_mqtt import connect_mqtt
