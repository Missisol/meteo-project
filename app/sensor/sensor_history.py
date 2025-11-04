from datetime import date, timedelta, datetime, timezone
from flask import current_app
from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import Bme280Outer, BmeHistory


def get_minmax_bme_data():
    for x in range(1, current_app.config['DAYS_RANGE'], 1):
        day = datetime.now().date() - timedelta(days=x) 
        print(f"date day: {day}")

        bq = sa.select(Bme280Outer).filter(sa.func.DATE(Bme280Outer.created_at) == day)
        bme_earlier_data = db.session.scalars(bq).all()

        hq = sa.select(BmeHistory).filter(sa.func.DATE(BmeHistory.date) == day)
        history_earlier_data = db.session.scalars(hq).first()

        try:
            if not bme_earlier_data:
                return
            elif bme_earlier_data and not history_earlier_data:
                min_temperature = min(bme_earlier_data, key=lambda x: x.temperature)
                max_temperature = max(bme_earlier_data, key=lambda x: x.temperature)
                min_humidity = min(bme_earlier_data, key=lambda x: x.humidity)
                max_humidity = max(bme_earlier_data, key=lambda x: x.humidity)
                min_pressure = min(bme_earlier_data, key=lambda x: x.pressure)
                max_pressure = max(bme_earlier_data, key=lambda x: x.pressure)


                history = BmeHistory(
                    min_temperature=min_temperature.temperature,
                    max_temperature=max_temperature.temperature,
                    min_humidity=min_humidity.humidity,
                    max_humidity=max_humidity.humidity,
                    min_pressure=min_pressure.pressure,
                    max_pressure=max_pressure.pressure,
                    min_temperature_time=min_temperature.created_at,
                    max_temperature_time=max_temperature.created_at,
                    min_humidity_time=min_humidity.created_at,
                    max_humidity_time=max_humidity.created_at,
                    min_pressure_time=min_pressure.created_at,
                    max_pressure_time=max_pressure.created_at,
                    date=day
                )

                db.session.add(history)
                db.session.commit()

                # delete_model_data(Bme280Outer, x)

            # elif bme_earlier_data and history_earlier_data:
            #     delete_model_data(Bme280Outer, x)
            else:
                print('BME data has already been saved')

        except Exception as e:
            print(e)


def delete_history_data(days):
    day = datetime.now().date() - timedelta(days=days) 
    del_stmt = sa.delete(BmeHistory).where(sa.func.DATE(BmeHistory.date) == day)

    db.session.execute(del_stmt)
    db.session.commit()


def delete_model_data(model, days):
    day = datetime.now().date() - timedelta(days=days) 
    del_stmt = sa.delete(model).filter(sa.func.DATE(model.created_at) == day)

    db.session.execute(del_stmt)
    db.session.commit()


def clear_db(model):
    for x in range(1, current_app.config['DAYS_RANGE'], 1):
        delete_model_data(model, x)
