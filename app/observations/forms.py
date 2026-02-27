import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length


# TODO унифицировать формы - убрать повторение
class ObservationForm(FlaskForm):
    created_at = DateField('Дата', default=datetime.date.today)
    cloudiness = SelectField('Облачность',
        choices=[
            ('clear', 'Ясно'),
            ('mostly_sunny', 'Преимущественно солнечно'),
            ('cloudy', 'Переменная облачность'),
            ('mostly_cloudy', 'Преимущественно облачно'),
            ('overcast', 'Пасмурно')
        ],
        validators=[DataRequired()])
    precipitation = SelectField('Осадки',
        choices=[
            ('none', 'Нет'),
            ('rain', 'Дождь'),
            ('snow', 'Снег'),
            ('sleet', 'Снег с дождем'),
            ('hail', 'Град')
        ],
        validators=[DataRequired()])
    precipitation_rate = SelectField('Интенсивность осадков',
        choices=[
            ('none', 'Нет'),
            ('light', 'Слабые'),
            ('moderate', 'Умеренные'),
            ('heavy', 'Сильные')
        ])
    snow_depth = StringField('Высота снежного покрова, см', 
        validators=[Length(min=0, max=4)])
    comment = StringField('Комментарий')
    submit = SubmitField('Добавить')

class EditForm(FlaskForm):
    id = HiddenField('id', id="editId")
    cloudiness = SelectField('Облачность',
        choices=[
            ('clear', 'Ясно'),
            ('mostly_sunny', 'Преимущественно солечно'),
            ('cloudy', 'Переменная облачность'),
            ('mostly_cloudy', 'Преимущественно облачно'),
            ('overcast', 'Пасмурно')
        ],
        validators=[DataRequired()])
    precipitation = SelectField('Осадки',
        choices=[
            ('none', 'Нет'),
            ('rain', 'Дождь'),
            ('snow', 'Снег'),
            ('sleet', 'Снег с дождем'),
            ('hail', 'Град')
        ],
        validators=[DataRequired()])
    precipitation_rate = SelectField('Интенсивность осадков',
        choices=[
            ('none', 'Нет'),
            ('light', 'Слабые'),
            ('moderate', 'Умеренные'),
            ('heavy', 'Сильные')
        ])
    snow_depth = StringField('Высота снежного покрова, см', 
        validators=[Length(min=0, max=4)])
    comment = StringField('Комментарий')
    submit = SubmitField('Сохранить')

class EmptyForm(FlaskForm):
    submit = SubmitField('Удалить')
