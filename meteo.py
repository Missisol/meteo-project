# gevent monkey patching ДО любых других импортов
from gevent import monkey
monkey.patch_all()

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import Bme280Rpi, Bme280Outer, Dht22, BmeHistory, Observations


app = create_app()

# Запуск MQTT клиента после создания app
from app.sensor import sensor_mqtt
sensor_mqtt.init_mqtt(app)


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'Bme280Rpi': Bme280Rpi, 'Bme280Outer': Bme280Outer, 'Dht22': Dht22, 'BmeHistory': BmeHistory, 'Observations': Observations}
