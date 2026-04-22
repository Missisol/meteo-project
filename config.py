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
    DAYS_RANGE = 11
    SAVE_INTERVAL = 60
    
    APP_ENV = os.environ.get('APP_ENV', 'production')

    # MQTT broker address
    MQTT_BROKER_URL = os.environ.get('RPI_URL')
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', 1883))
    WS_BROKER_PORT = int(os.environ.get('WS_BROKER_PORT', 9001))

    # MQTT topics
    MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID', 'sensor')
    MQTT_TOPIC_ESP8266 = os.environ.get('MQTT_TOPIC_ESP8266', 'test')
    MQTT_TOPIC_BME280 = os.environ.get('MQTT_TOPIC_BME280')
    MQTT_TOPIC_DHT22 = os.environ.get('MQTT_TOPIC_DHT22')
    
    # Telegram
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
    CHAT_ID = os.environ.get('CHAT_ID', '')
    



