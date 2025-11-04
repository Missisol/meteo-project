import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'meteo.db')
    LANGUAGES = ['ru', 'en']
    TIMEZONE = 'Europe/Moscow'
    ITEMS_PER_PAGE = 16
    HISTORY_ITEMS_LIMIT = 10
    MQTT_TOPIC_BME280 = os.environ.get('MQTT_TOPIC_BME280')
    MQTT_TOPIC_DHT22 = os.environ.get('MQTT_TOPIC_DHT22')
    DAYS_RANGE = 11
    SAVE_INTERVAL = 60

