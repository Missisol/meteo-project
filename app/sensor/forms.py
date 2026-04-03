from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import Length, Optional


class Bme280OuterEditForm(FlaskForm):
    """Форма для редактирования записи BME280 Outer."""
    id = HiddenField('id', id="editId")
    temperature = StringField('Температура, °C', validators=[Length(min=0, max=10)])
    humidity = StringField('Влажность, %', validators=[Length(min=0, max=10)])
    pressure = StringField('Давление, мм.рт.ст.', validators=[Length(min=0, max=10)])
    submit = SubmitField('Сохранить')


class EmptyForm(FlaskForm):
    submit = SubmitField('Удалить')
