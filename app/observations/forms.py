import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length


# Общие варианты выбора для полей
CLOUDINESS_CHOICES = [
    ('clear', 'Ясно'),
    ('mostly_sunny', 'Преимущественно солнечно'),
    ('cloudy', 'Переменная облачность'),
    ('mostly_cloudy', 'Преимущественно облачно'),
    ('overcast', 'Пасмурно')
]

PRECIPITATION_CHOICES = [
    ('none', 'Нет'),
    ('rain', 'Дождь'),
    ('snow', 'Снег'),
    ('sleet', 'Снег с дождем'),
    ('hail', 'Град')
]

PRECIPITATION_RATE_CHOICES = [
    ('none', 'Нет'),
    ('light', 'Слабые'),
    ('moderate', 'Умеренные'),
    ('heavy', 'Сильные')
]


class BaseObservationForm(FlaskForm):
    """Базовый класс с общими полями для наблюдений."""
    cloudiness = SelectField('Облачность',
        choices=CLOUDINESS_CHOICES,
        validators=[DataRequired()])
    precipitation = SelectField('Осадки',
        choices=PRECIPITATION_CHOICES,
        validators=[DataRequired()])
    precipitation_rate = SelectField('Интенсивность осадков',
        choices=PRECIPITATION_RATE_CHOICES)
    snow_depth = StringField('Высота снежного покрова, см', 
        validators=[Length(min=0, max=4)])
    comment = StringField('Комментарий')


class ObservationForm(BaseObservationForm):
    """Форма для создания нового наблюдения."""
    created_at = DateField('Дата', default=datetime.date.today)
    submit = SubmitField('Добавить')


class EditForm(BaseObservationForm):
    """Форма для редактирования наблюдения."""
    id = HiddenField('id', id="editId")
    submit = SubmitField('Сохранить')

class EmptyForm(FlaskForm):
    submit = SubmitField('Удалить')
