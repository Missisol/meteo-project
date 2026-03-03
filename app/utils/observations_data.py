observations_table = {
  'th': ['Дата', 'Облачность', 'Осадки', 'Интенсивность осадков', 'Высота снежного покрова, см', 'Комментарий',  'Действия'],
  'td': ['created_at', 'cloudiness', 'precipitation', 'precipitation_rate', 'snow_depth', 'comment', 'actions']
}

cloudiness_map = {
  'clear': 'ясно',
  'mostly_sunny': 'преимущественно солнечно',
  'cloudy': 'переменная облачность',
  'mostly_cloudy': 'преимущественно облачно',
  'overcast': 'пасмурно',
}

precipitation_map = {
  'none': 'нет',
  'rain': 'дождь',
  'snow': 'снег',
  'sleet': 'снег с дождем',
  'hail': 'град',
}

precipitation_rate_map = {
  'none': 'нет',
  'light': 'слабые',
  'moderate': 'умеренные',
  'heavy': 'сильные',
}

observations_map = {
  'cloudiness': cloudiness_map,
  'precipitation': precipitation_map,
  'precipitation_rate': precipitation_rate_map,
}

combined_observations_table = {
  'th': ['Дата', 'Облачность', 'Осадки', 'Интенсивность осадков', 'Высота снежного покрова, см', 'Мин. темп., °C', 'Макс. темп., °C', 'Комментарий'],
  'td': ['date', 'cloudiness', 'precipitation', 'precipitation_rate', 'snow_depth', 'min_temperature', 'max_temperature', 'comment']
}