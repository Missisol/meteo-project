from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length


class ObservationForm(FlaskForm):
    created_at = DateField('Дата')
    cloudiness = SelectField('Облачность',
        choices=[
            ('clear', 'Ясно'),
            ('cloudy', 'Облачно'),
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
    submit = SubmitField('Добавить')

class EditForm(FlaskForm):
    id = HiddenField('id', id="editId")
    cloudiness = SelectField('Облачность',
        choices=[
            ('clear', 'Ясно'),
            ('cloudy', 'Облачно'),
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
    submit = SubmitField('Сохранить')

class EmptyForm(FlaskForm):
    submit = SubmitField('Удалить')

class FilterForm(FlaskForm):
    start_date = DateField('Начальная дата', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Конечная дата', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Фильтровать')
    clear = SubmitField('Очистить')