main_menu = [
    { 'url': 'main.index', 'text': 'Датчик погоды'},   
    { 'url': 'sensor.sensors', 'text': 'Датчики в доме'},   
    { 'text': 'Таблицы', 'nested': [
        { 'url': 'sensor.bme_history', 'text': 'BME280 история'},
        { 'url': 'sensor.bme280_outer', 'text': 'BME280 внешний'},   
        { 'url': 'sensor.dht22_outer', 'text': 'DHT22 внешние'},   
        # { 'url': 'sensor.bme280_rpi', 'text': 'BME280 RPI'},   
    ]},
    { 'url': 'observations.observations', 'text': 'Наблюдения'},   
]

theme_switcher = [
    { 'value': 'light', 'pressed': 'false', 'icon': 'sun' },
    { 'value': 'light dark', 'pressed': 'false', 'text': 'Авто' },
    { 'value': 'dark', 'pressed': 'false', 'icon': 'moon' },
]

form_buttons = [
    { 'type': 'submit', 'id': 'button-submit', 'value': 'Задать период', 'class': 'button button--blue' },
    { 'type': 'reset', 'id': 'button-reset', 'value': 'Очистить', 'class': 'button button--invert' },
]

