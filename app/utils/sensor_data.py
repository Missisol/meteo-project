list_date = [
     {
        'dataName': "Даные на", 
        'data': 'date',
    },
]

list1 = [
    {
        'dataName': "Температура, &deg;C",
        'data': 'temperature',
    }, 
    {
        'dataName': "Влажность, %", 
        'data': 'humidity',
    }, 
]

list2 = [
     {
        'dataName': "Давление, мм.рт.ст.", 
        'data': 'pressure',
    },
]

list3 = [*list1, *list2]

list_dht = [*list_date, *list1]

list_bme = [*list_date, *list3]

prefix_list = ['rpi', 'bme', 'dht1', 'dht2']
sensors_list = ['rpi', 'dht1', 'dht2']
weather_list = ['bme']

bme_rpi_table = {
    'th': ['Дата - время (МСК)', 'Температура, &deg;C', 'Влажность, %', 'Давление, мм.рт.ст.'],
    'td': ['created_at', 'temperature', 'humidity', 'pressure']
}

bme_outer_data = {
    'th': ['Дата - время (МСК)', 'Температура, &deg;C', 'Влажность, %', 'Давление, мм.рт.ст.', 'Действия'],
    'td': ['created_at', 'temperature', 'humidity', 'pressure', 'actions']
}

bme_outer_table = {
    'th': ['Дата - время (МСК)', 'Температура, &deg;C', 'Влажность, %', 'Давление, мм.рт.ст.'],
    'td': ['created_at', 'temperature', 'humidity', 'pressure']
}

dht_outer_table = {
    'th': ['Дата - время (МСК)', 'Температура 1, &deg;C', 'Влажность 1, %', 'Температура 2, &deg;C', 'Влажность 2, %'],
    'td': ['created_at', 'temperature1', 'humidity1', 'temperature2', 'humidity2']
}

history_table = {
    'th': [
      'Дата', 
      'Температура мин., &deg;C', 
      'Время', 
      'Температура макс., &deg;C', 
      'Время',
      'Влажность мин., %', 
      'Время',
      'Влажность макс., %', 
      'Время',
      'Давление мин., мм.рт.ст.', 
      'Время',
      'Давление макс., мм.рт.ст.',
      'Время',
      ],
    'td': [
        'date', 
        'min_temperature', 
        'min_temperature_time', 
        'max_temperature', 
        'max_temperature_time', 
        'min_humidity', 
        'min_humidity_time', 
        'max_humidity', 
        'max_humidity_time', 
        'min_pressure', 
        'min_pressure_time', 
        'max_pressure',
        'max_pressure_time',
      ]
}
