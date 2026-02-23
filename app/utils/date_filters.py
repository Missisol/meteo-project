"""
Утилиты для фильтрации данных по датам с учетом часовых поясов.
"""
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from flask import request
import sqlalchemy as sa


def local_date_to_utc_range(local_date: date, timezone_str: str = 'Europe/Moscow') -> tuple[datetime, datetime]:
    """
    Преобразует локальную дату в диапазон UTC datetime.
    
    Args:
        local_date: Дата в локальном часовом поясе
        timezone_str: Часовой пояс (по умолчанию 'Europe/Moscow')
    
    Returns:
        Кортеж (start_utc, end_utc) - начало и конец дня в UTC (без tzinfo)
    """
    tz = ZoneInfo(timezone_str)
    
    # Начало дня в локальном часовом поясе (00:00:00)
    start_local = datetime.combine(local_date, time.min, tzinfo=tz)
    
    # Конец дня в локальном часовом поясе (начало следующего дня, 00:00:00)
    end_local = datetime.combine(local_date + timedelta(days=1), time.min, tzinfo=tz)
    
    # Преобразование в UTC и удаление tzinfo для совместимости с SQLAlchemy
    start_utc = start_local.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    end_utc = end_local.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    
    return start_utc, end_utc


def apply_date_filters(query, model, filter_form, timezone_str: str, date_field_type: str = 'datetime'):
    """
    Применяет фильтрацию по датам к запросу.
    
    Args:
        query: SQLAlchemy запрос
        model: Модель SQLAlchemy
        filter_form: Форма фильтрации с полями start_date и end_date
        timezone_str: Часовой пояс для конвертации дат
        date_field_type: Тип поля даты ('datetime' для created_at, 'date' для date)
    
    Returns:
        Кортеж (query, url_args, start_date_str, end_date_str, start_date, end_date)
    """
    from flask import flash
    
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
    else:
        # Apply date filters
        if date_field_type == 'datetime':
            # Для полей типа datetime (например, created_at) с учетом часового пояса
            if start_date:
                start_utc, _ = local_date_to_utc_range(start_date, timezone_str)
                query = query.where(model.created_at >= start_utc)
            
            if end_date:
                _, end_utc = local_date_to_utc_range(end_date, timezone_str)
                query = query.where(model.created_at < end_utc)
        elif date_field_type == 'date':
            # Для полей типа date (например, date) без конвертации
            if start_date:
                query = query.where(model.date >= start_date)
            
            if end_date:
                end_date_plus_one = end_date + timedelta(days=1)
                query = query.where(model.date < end_date_plus_one)
    
    # Build URL args for pagination
    url_args = {}
    if start_date_str:
        url_args['start_date'] = start_date_str
    if end_date_str:
        url_args['end_date'] = end_date_str
    
    return query, url_args, start_date_str, end_date_str, start_date, end_date
