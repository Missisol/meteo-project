import json
import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from paho.mqtt import client as mqtt

from app import db, models, socketio
from app.sensor import telegram_sender

logger = logging.getLogger(__name__)

# Константы валидации
VALIDATION_THRESHOLDS = {
    'temperature': (float('-inf'), 100),
    'humidity': (0, 100),
    'pressure': (0, 800),
}


@dataclass
class SensorConfig:
    """Конфигурация MQTT клиента."""
    broker_url: str
    broker_port: int = 1883
    topic_bme280: str = ''
    topic_dht22: str = ''


@dataclass
class SensorState:
    """Состояние датчиков и время последнего сохранения."""
    latest_bme280: Optional[dict] = None
    latest_dht22: Optional[dict] = None
    last_bme280_save: Optional[datetime] = None
    last_dht22_save: Optional[datetime] = None
    last_dht22_slot: Optional[int] = None  # Последний сохранённый слот (3 или 15)


class MQTTSensorClient:
    """MQTT клиент для обработки данных с датчиков BME280 и DHT22."""
    
    # Слоты сохранения DHT22 (часы)
    DHT22_SLOTS = [3, 15]

    def __init__(self, flask_app):
        self.app = flask_app
        self._config: Optional[SensorConfig] = None
        self._state = SensorState()
        self._mqttc: Optional[mqtt.Client] = None
        self._lock = threading.Lock()

    def init(self):
        """Инициализация MQTT клиента."""
        self._load_config()
        self._start_mqtt_client()
        logger.info(f"MQTT client initialized, connecting to {self._config.broker_url}")

    def _load_config(self):
        """Загрузка конфигурации из переменных окружения."""
        self._config = SensorConfig(
            broker_url=os.environ['RPI_URL'],
            broker_port=1883,
            topic_bme280=os.environ['MQTT_TOPIC_BME280'],
            topic_dht22=os.environ['MQTT_TOPIC_DHT22'],
        )

    # --- Обработчики MQTT ---

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int):
        """Обработчик подключения к брокеру."""
        if rc == 0:
            logger.info("MQTT connected successfully")
            client.subscribe(self._config.topic_bme280, qos=1)
            client.subscribe(self._config.topic_dht22, qos=1)
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        """Обработчик входящих сообщений."""
        topic = message.topic
        payload = message.payload
        
        logger.debug(f"Received from {topic}: {payload}")
        socketio.emit('other_message', payload)

        try:
            if topic == self._config.topic_bme280:
                self._handle_bme280(payload)
            elif topic == self._config.topic_dht22:
                self._handle_dht22(payload)
        except Exception as e:
            logger.exception(f"Error processing message from {topic}: {e}")

    # --- Обработчики датчиков ---

    def _handle_bme280(self, payload: bytes):
        """Обработка сообщений от BME280."""
        logger.debug("BME280 readings update")
        socketio.emit('bme_message', payload.decode())

        data = self._parse_payload(payload)
        self._validate_bme280_data(data)

        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        pressure = round(int(data['pressure']))

        # Обновляем последние данные
        self._state.latest_bme280 = {
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
            'created_at': datetime.now(timezone.utc)
        }

        # Проверяем, нужно ли сохранять (раз в час)
        if self._should_save_bme280():
            self._save_bme280_and_notify(temperature, humidity, pressure)

    def _handle_dht22(self, payload: bytes):
        """Обработка сообщений от DHT22."""
        logger.debug("DHT22 readings update")
        socketio.emit('dht_message', payload.decode())

        data = self._parse_payload(payload)
        self._validate_dht22_data(data)

        temperature_1 = float(data['temperature1'])
        humidity_1 = float(data['humidity1'])
        temperature_2 = float(data['temperature2'])
        humidity_2 = float(data['humidity2'])

        self._state.latest_dht22 = {
            'temperature1': temperature_1,
            'humidity1': humidity_1,
            'temperature2': temperature_2,
            'humidity2': humidity_2,
            'created_at': datetime.now(timezone.utc)
        }

        # Сохранение дважды в день (03:00 и 15:00)
        if self._should_save_dht22():
            self._save_dht22()

    # --- Парсинг и валидация ---

    def _parse_payload(self, payload: bytes) -> dict:
        """Парсинг JSON payload."""
        try:
            return json.loads(payload.decode())
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
            raise ValueError(f"Invalid payload format") from e

    def _validate_bme280_data(self, data: dict):
        """Валидация данных BME280."""
        required = ('temperature', 'humidity', 'pressure')
        for key in required:
            if key not in data:
                raise KeyError(f"Missing required field: {key}")

    def _validate_dht22_data(self, data: dict):
        """Валидация данных DHT22."""
        required = ('temperature1', 'humidity1', 'temperature2', 'humidity2')
        for key in required:
            if key not in data:
                raise KeyError(f"Missing required field: {key}")

    def _is_valid_value(self, value: float, sensor_type: str) -> bool:
        """Проверка значения на допустимость."""
        min_val, max_val = VALIDATION_THRESHOLDS.get(sensor_type, (float('-inf'), float('inf')))
        return min_val < value < max_val

    # --- Логика сохранения ---

    def _should_save_bme280(self) -> bool:
        """Проверка, нужно ли сохранять данные BME280 (раз в час)."""
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        last_save = self._state.last_bme280_save
        return last_save is None or last_save < current_hour

    def _should_save_dht22(self) -> bool:
        """Проверка, нужно ли сохранять данные DHT22 (в 03:00 и 15:00)."""
        now = datetime.now()
        current_hour = now.hour
        
        # Определяем текущий активный слот
        current_slot = None
        for slot in sorted(self.DHT22_SLOTS):
            if current_hour >= slot:
                current_slot = slot
            else:
                break
        
        if current_slot is None:
            current_slot = self.DHT22_SLOTS[0]
        
        # Проверяем, был ли уже сохранён этот слот сегодня
        if self._state.last_dht22_slot == current_slot and self._state.last_dht22_save is not None:
            if self._state.last_dht22_save.date() == now.date():
                return False
        
        # Проверяем, что мы уже прошли время слота (прошла хотя бы минута)
        slot_time = now.replace(hour=current_slot, minute=1, second=0, microsecond=0)
        if now < slot_time:
            return False
        
        return True

    def _save_bme280_and_notify(self, temperature: float, humidity: float, pressure: int):
        """Сохранение данных BME280 и отправка уведомления."""
        if not self._is_valid_value(temperature, 'temperature'):
            logger.warning("Invalid temperature value, skipping save")
            return
        if not self._is_valid_value(humidity, 'humidity'):
            logger.warning("Invalid humidity value, skipping save")
            return
        if not self._is_valid_value(pressure, 'pressure'):
            logger.warning("Invalid pressure value, skipping save")
            return

        record = models.Bme280Outer(
            temperature=temperature,
            humidity=humidity,
            pressure=pressure
        )
        self._save_to_db(record)
        self._state.last_bme280_save = datetime.now()
        
        logger.info(f"BME280 saved: T={temperature}, H={humidity}, P={pressure}")
        
        # Отправка в Telegram
        telegram_sender.get_telegram_sender().send_notification(temperature, humidity, pressure)

    def _save_dht22(self):
        """Сохранение данных DHT22."""
        data = self._state.latest_dht22
        if data is None:
            return
            
        # Определяем текущий слот для записи
        now = datetime.now()
        current_hour = now.hour
        current_slot = None
        for slot in sorted(self.DHT22_SLOTS):
            if current_hour >= slot:
                current_slot = slot
            else:
                break
        if current_slot is None:
            current_slot = self.DHT22_SLOTS[0]
        
        record = models.Dht22(
            temperature1=data['temperature1'],
            humidity1=data['humidity1'],
            temperature2=data['temperature2'],
            humidity2=data['humidity2'],
            created_at=data['created_at']
        )
        self._save_to_db(record)
        self._state.last_dht22_save = now
        self._state.last_dht22_slot = current_slot
        
        logger.info(f"DHT22 saved: T1={data['temperature1']}, H1={data['humidity1']}")

    def _save_to_db(self, record):
        """Сохранение записи в БД."""
        with self.app.app_context():
            db.session.add(record)
            db.session.commit()

    # --- Запуск MQTT ---

    def _mqtt_loop(self):
        """Запуск MQTT цикла в отдельном потоке."""
        self._mqttc.connect_async(self._config.broker_url, self._config.broker_port, 60)
        self._mqttc.loop_forever()

    def _start_mqtt_client(self):
        """Запуск MQTT клиента в фоновом потоке."""
        self._mqttc = mqtt.Client(client_id="sensor", clean_session=True)
        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_message = self._on_message
        
        thread = threading.Thread(target=self._mqtt_loop, daemon=True)
        thread.start()


# Глобальный экземпляр
_mqtt_client: Optional[MQTTSensorClient] = None


def init_mqtt(flask_app):
    """Инициализация MQTT клиента."""
    global _mqtt_client
    telegram_sender.init_telegram(flask_app)
    _mqtt_client = MQTTSensorClient(flask_app)
    _mqtt_client.init()


def get_mqtt_client() -> MQTTSensorClient:
    """Получение экземпляра MQTT клиента."""
    if _mqtt_client is None:
        raise RuntimeError("MQTT client not initialized")
    return _mqtt_client
