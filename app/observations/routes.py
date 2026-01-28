from flask import render_template, request, url_for, current_app, redirect, flash, abort, jsonify
import sqlalchemy as sa
from flask_babel import format_datetime
from datetime import datetime, timezone

from app import db
from app.observations import bp
from app.models import Observations
from app.utils.observations_data import observations_table, observations_map
from app.observations.forms import EmptyForm, ObservationForm, EditForm, FilterForm

@bp.app_template_filter('datetimeformat')
def datetimeformat(value):
    # return format_datetime(value, 'd.MM.YY, HH:mm')
    return datetime.strftime(value, '%d.%m.%y, %H:%M')


@bp.route('/observations')
def observations():
  add_form = ObservationForm()
  empty_form = EmptyForm()
  edit_form = EditForm()
  filter_form = FilterForm()
  
  page = request.args.get('page', 1, type=int)
  start_date_str = request.args.get('start_date')
  end_date_str = request.args.get('end_date')
  
  # Validate date range
  start_date = None
  end_date = None
  
  if start_date_str:
    try:
      start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
      filter_form.start_date.data = start_date
    except ValueError:
      pass
  
  if end_date_str:
    try:
      end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
      filter_form.end_date.data = end_date
    except ValueError:
      pass
  
  # Check if start date is greater than end date
  if start_date and end_date and start_date > end_date:
    flash('Дата начала периода больше даты конца периода. Пожалуйста, проверьте введенные даты.', 'warning')
    # Don't apply filters if dates are invalid
    query = sa.select(Observations)
  else:
    # Build query
    query = sa.select(Observations)
    
    # Apply date filters
    if start_date:
      query = query.where(sa.func.date(Observations.created_at) >= start_date)
    
    if end_date:
      query = query.where(sa.func.date(Observations.created_at) <= end_date)
  
  query = query.order_by(Observations.created_at.desc())
  
  data = db.paginate(query, page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
  
  # Build pagination URLs with filter parameters
  url_args = {}
  if start_date_str:
    url_args['start_date'] = start_date_str
  if end_date_str:
    url_args['end_date'] = end_date_str
  
  next_url = url_for('observations.observations', page=data.next_num, **url_args) \
      if data.has_next else None
  prev_url = url_for('observations.observations', page=data.prev_num, **url_args) \
      if data.has_prev else None

  return render_template('observations/observations.html', data=data.items, next_url=next_url, prev_url=prev_url, table=observations_table, add_table=observations_map, empty_form=empty_form, add_form=add_form, edit_form=edit_form, filter_form=filter_form, start_date=start_date_str, end_date=end_date_str)


@bp.route('/observations/new', methods=['GET', 'POST'])
def create_observation():
    if request.method == 'POST':
        cloudiness = request.form.get('cloudiness', 'clear')
        precipitation = request.form.get('precipitation', 'none')
        precipitation_rate = request.form.get('precipitation_rate', 'none')
        snow_depth = request.form.get('snow_depth', 0, type=int)
        created_at_str = request.form.get('created_at')
        created_at = datetime.strptime(created_at_str, '%Y-%m-%d') if created_at_str else datetime.now()
        
        # Проверка на существование записи с такой же датой (без учета времени)
        query = sa.select(Observations).where(
            sa.func.date(Observations.created_at) == created_at.date()
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


@bp.route('/observations/<int:id>/delete', methods=['POST'])
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


@bp.route('/observations/<int:id>/data', methods=['GET'])
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


@bp.route('/observations/update', methods=['POST'])
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
