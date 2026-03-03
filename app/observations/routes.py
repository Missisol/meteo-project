from flask import render_template, request, url_for, current_app, redirect, flash, abort, jsonify
import sqlalchemy as sa
from flask_babel import format_datetime
from datetime import datetime, timezone

from app import db
from app.observations import bp
from app.models import Observations, BmeHistory
from app.utils.observations_data import observations_table, observations_map
from app.observations.forms import EmptyForm, ObservationForm, EditForm
from app.main.forms import FilterForm
from app.utils.date_filters import apply_date_filters


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


@bp.route('/observations/new', methods=['GET', 'POST'])
def create_observation():
    if request.method == 'POST':
        cloudiness = request.form.get('cloudiness', 'clear')
        precipitation = request.form.get('precipitation', 'none')
        precipitation_rate = request.form.get('precipitation_rate', 'none')
        snow_depth = request.form.get('snow_depth', 0, type=int)
        created_at_str = request.form.get('created_at')
        comment = request.form.get('comment')
        
        # Если дата введена пользователем, создаем из неё datetime как начало дня в UTC
        created_at = datetime.strptime(created_at_str, '%Y-%m-%d') if created_at_str else datetime.now(timezone.utc)

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
            comment=comment if comment is not None else '',
        )
        
        db.session.add(observation)
        db.session.commit()
        flash('Наблюдение успешно добавлено', 'success')
        return redirect(url_for('observations.observations'))
    
    # return render_template('observations/observations.html')


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
    # return render_template('observations/observations.html')


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
        'snow_depth': observation.snow_depth,
        'comment': observation.comment,
    })


@bp.route('/observations/update', methods=['POST'])
def update_observation():
    id = request.form.get('id')
    if not id:
        flash('ID is required', 'warning')
        return jsonify({'success': False, 'error': 'ID is required'})
    
    observation = db.session.get(Observations, id)
    if observation is None:
        flash('Observation not found', 'warning')
        return jsonify({'success': False, 'error': 'Observation not found'})
    
    cloudiness = request.form.get('cloudiness')
    precipitation = request.form.get('precipitation')
    precipitation_rate = request.form.get('precipitation_rate')
    snow_depth = request.form.get('snow_depth', type=int)
    comment = request.form.get('comment')
    
    if cloudiness:
        observation.cloudiness = cloudiness
    if precipitation:
        observation.precipitation = precipitation
    if precipitation_rate is not None:
        observation.precipitation_rate = precipitation_rate
    if snow_depth is not None:
        observation.snow_depth = snow_depth
    if comment is not None:
        observation.comment = comment
    
    try:
        db.session.commit()
        flash('Наблюдение успешно обновлено', 'success')
        return redirect(url_for('observations.observations'))

    except Exception as e:
        db.session.rollback()
        flash('Произошла ошибка при обновлении наблюдения', 'warning')
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/table/observations_combined')
def observations_combined():
    from datetime import datetime, timezone
    import sqlalchemy as sa
    from app.utils.date_filters import apply_date_filters
    from app.utils.observations_data import combined_observations_table
    
    filter_form = FilterForm()
    
    # Получаем параметры пагинации
    page = request.args.get('page', 1, type=int)
    
   # Запрос для объединения данных из двух таблиц
    # Используем LEFT JOIN, чтобы показать все наблюдения, даже если нет данных о температуре
    # Важно: используем select_from для корректного объединения моделей
    query = sa.select(Observations, BmeHistory).select_from(
        Observations
    ).outerjoin(
        BmeHistory,
        sa.func.date(Observations.created_at) == sa.func.date(BmeHistory.date)
    ).order_by(Observations.created_at.desc())
    
    # Применяем фильтры по дате
    query, url_args, start_date_str, end_date_str, start_date, end_date = apply_date_filters(
        query, Observations, filter_form, current_app.config['TIMEZONE'], 'datetime'
    )
    
    # Добавляем дополнительную фильтрацию для исключения сегодняшней даты (нужны только предыдущие дни)
    today_start = datetime.now(timezone.utc).date()
    query = query.filter(sa.func.date(Observations.created_at) < today_start)
    
    # Выполняем запрос с пагинацией
    # Используем execute + paginate для корректной работы с составными запросами
    paginated = db.paginate(query, page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    
    # Получаем ID записей для ручной пагинации
    # Это необходимо, так как select с двумя моделями может некорректно обрабатываться
    obs_ids = [row.id for row in paginated.items]
    
    # Выполняем отдельный запрос для получения данных с JOIN
    if obs_ids:
        data_query = sa.select(Observations, BmeHistory).select_from(
            Observations
        ).outerjoin(
            BmeHistory,
            sa.func.date(Observations.created_at) == sa.func.date(BmeHistory.date)
        ).where(Observations.id.in_(obs_ids)).order_by(Observations.created_at.desc())
        
        rows = db.session.execute(data_query).all()
    else:
        rows = []
    
    # Преобразуем результаты в нужный формат
    combined_data = []
    for row in rows:
        # row - это кортеж (observations_instance, bme_history_instance)
        obs, bme = row
        
        # Извлекаем дату из наблюдения (берем только дату, без времени)
        obs_date = obs.created_at.date()
        
        # Формируем объект с объединенными данными
        combined_item = {
            'date': obs_date,
            'cloudiness': obs.cloudiness,
            'precipitation': obs.precipitation,
            'precipitation_rate': obs.precipitation_rate,
            'snow_depth': obs.snow_depth,
            'comment': obs.comment,
            'min_temperature': bme.min_temperature if bme else None,
            'max_temperature': bme.max_temperature if bme else None
        }
        combined_data.append(combined_item)
    
    next_url = url_for('observations.observations_combined', page=paginated.next_num, **url_args) \
        if paginated.has_next else None
    prev_url = url_for('observations.observations_combined', page=paginated.prev_num, **url_args) \
        if paginated.has_prev else None

    return render_template('observations/observations_combined.html',
                          data=combined_data,
                          next_url=next_url,
                          prev_url=prev_url,
                          table=combined_observations_table,
                          filter_form=filter_form,
                          start_date=start_date_str,
                          end_date=end_date_str,
                          add_table=observations_map)
