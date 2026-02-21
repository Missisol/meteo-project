from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import DataRequired


class FilterForm(FlaskForm):
    start_date = DateField('Начальная дата', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Конечная дата', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Фильтровать')
