from flask import render_template, request, url_for, current_app, redirect, flash, abort, jsonify
import sqlalchemy as sa
from flask_babel import format_datetime
from datetime import datetime, timezone

from app import db
from app.observations import bp
from app.models import Observations
from app.utils.observations_data import observations_table, observations_map
from app.observations.forms import EmptyForm, ObservationForm, EditForm
from app.main.forms import FilterForm
from app.utils.date_filters import local_date_to_utc_range, apply_date_filters


@bp.route('/observations')
def observations():
  add_form = ObservationForm()
  empty_form = EmptyForm()
  edit_form = EditForm()
  filter_form = FilterForm()
  
  page = request.args.get('page', 1, type=int)
  
  query = sa.select(Observations)
  query, url_args, start_date_str, end_date_str, start_date, end_date = apply_date_filters(
    query, Observations, filter_form, current_app.config['TIMEZONE'], 'datetime'
  )
  
  query = query.order_by(Observations.created_at.desc())
  
  data = db.paginate(query, page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
  
  next_url = url_for('observations.observations', page=data.next_num, **url_args) \
      if data.has_next else None
  prev_url = url_for('observations.observations', page=data.prev_num, **url_args) \
      if data.has_prev else None

  return render_template('observations/observations.html', data=data.items, next_url=next_url, prev_url=prev_url, table=observations_table, add_table=observations_map, empty_form=empty_form, add_form=add_form, edit_form=edit_form, filter_form=filter_form, start_date=start_date_str, end_date=end_date_str)


@bp.route('/api/observations/new', methods=['GET', 'POST'])
def create_observation():
    if request.method == 'POST':
        cloudiness = request.form.get('cloudiness', 'clear')
        precipitation = request.form.get('precipitation', 'none')
        precipitation_rate = request.form.get('precipitation_rate', 'none')
        snow_depth = request.form.get('snow_depth', 0, type=int)
        created_at_str = request.form.get('created_at')
        
        if created_at_str:
            # Если дата введена пользователем, интерпретируем её как локальную дату
            local_date = datetime.strptime(created_at_str, '%Y-%m-%d').date()
            # Создаем datetime как начало дня в локальном часовом поясе и конвертируем в UTC
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(current_app.config['TIMEZONE'])
            start_local = datetime.combine(local_date, datetime.min.time(), tzinfo=tz)
            created_at = start_local.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
        else:
            created_at = datetime.now(timezone.utc)
        
        # Проверка на существование записи с такой же датой (без учета времени)
        # Используем диапазон UTC для корректного сравнения
        start_utc, end_utc = local_date_to_utc_range(created_at.date(), current_app.config['TIMEZONE'])
        query = sa.select(Observations).where(
            Observations.created_at >= start_utc,
            Observations.created_at < end_utc
        )
        existing_observation = db.session.scalar(query)

        if existing_observation:
            flash(f'Запись с датой {format_datetime(existing_observation.created_at, "d.MM.YY")} уже существует. Пожалуйста, отредактируйте её.', 'warning')
            return redirect(url_for('observations.observations'))
        
        observation = Observations(
            cloudiness=cloudiness,
            precipitation=precipitation,
            precipitation_rate=precipitation_rate,
            snow_depth=snow_depth if snow_depth is not None else 0,
            created_at=created_at,
        )
        
        db.session.add(observation)
        db.session.commit()
        flash('Наблюдение успешно добавлено', 'success')
        return redirect(url_for('observations.observations'))
    
    return render_template('observations/observations.html')


@bp.route('/api/observations/<int:id>/delete', methods=['POST'])
def delete_observation(id):
    form = EmptyForm()
    if form.validate_on_submit():
        observation = db.session.scalar(sa.select(Observations).where(Observations.id == id))
        if observation:
            observation.delete_observation()
            db.session.commit()
            flash('Наблюдение успешно удалено', 'success')
            return redirect(url_for('observations.observations'))
    return render_template('observations/observations.html')


@bp.route('/api/observations/<int:id>/data', methods=['GET'])
def get_observation_data(id):
    observation = db.session.get(Observations, id)
    if observation is None:
        abort(404)
    
    return jsonify({
        'created_at': observation.created_at.strftime('%d.%m.%y'),
        'cloudiness': observation.cloudiness,
        'precipitation': observation.precipitation,
        'precipitation_rate': observation.precipitation_rate,
        'snow_depth': observation.snow_depth
    })


@bp.route('/api/observations/update', methods=['POST'])
def update_observation():
    id = request.form.get('id')
    if not id:
        return jsonify({'success': False, 'error': 'ID is required'})
    
    observation = db.session.get(Observations, id)
    if observation is None:
        return jsonify({'success': False, 'error': 'Observation not found'})
    
    cloudiness = request.form.get('cloudiness')
    precipitation = request.form.get('precipitation')
    precipitation_rate = request.form.get('precipitation_rate')
    snow_depth = request.form.get('snow_depth', type=int)
    
    if cloudiness:
        observation.cloudiness = cloudiness
    if precipitation:
        observation.precipitation = precipitation
    if precipitation_rate is not None:
        observation.precipitation_rate = precipitation_rate
    if snow_depth is not None:
        observation.snow_depth = snow_depth
    
    try:
        db.session.commit()
        flash('Наблюдение успешно обновлено', 'success')
        return redirect(url_for('observations.observations'))

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
