from datetime import datetime, timezone, date
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class Bme280Rpi(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    temperature: so.Mapped[float] = so.mapped_column(sa.Float)
    humidity: so.Mapped[float] = so.mapped_column(sa.Float)
    pressure: so.Mapped[int] = so.mapped_column(sa.Integer)
    created_at: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return '<temperature {}>'.format(self.temperature)
    

class Bme280Outer(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    temperature: so.Mapped[float] = so.mapped_column(sa.Float)
    humidity: so.Mapped[float] = so.mapped_column(sa.Float)
    pressure: so.Mapped[int] = so.mapped_column(sa.Integer)
    created_at: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    date: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc).date())
    # date: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: date.today())
    
    def __repr__(self):
        return f"temperature: {self.temperature}, humidity: {self.humidity}, pressure: {self.pressure}, created_at: {self.created_at}, date: {self.date}"
        

class Dht22(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    temperature1: so.Mapped[float] = so.mapped_column(sa.Float)
    humidity1: so.Mapped[float] = so.mapped_column(sa.Float)
    temperature2: so.Mapped[float] = so.mapped_column(sa.Float)
    humidity2: so.Mapped[float] = so.mapped_column(sa.Float)
    created_at: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"temperature-1: {self.temperature1}, humidity-1: {self.humidity1}, temperature-2: {self.temperature2}, humidity-2: {self.humidity2}, created_at: {self.created_at}"


class BmeHistory(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[datetime] = so.mapped_column(
    index=True, default=lambda: datetime.now(timezone.utc).date())
    min_temperature: so.Mapped[float] = so.mapped_column(sa.Float)
    max_temperature: so.Mapped[float] = so.mapped_column(sa.Float)
    min_humidity: so.Mapped[float] = so.mapped_column(sa.Float)
    max_humidity: so.Mapped[float] = so.mapped_column(sa.Float)
    min_pressure: so.Mapped[int] = so.mapped_column(sa.Integer)
    max_pressure: so.Mapped[int] = so.mapped_column(sa.Integer)
    min_temperature_time: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=None, nullable=True)
    max_temperature_time: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=None, nullable=True)
    min_humidity_time: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=None, nullable=True)
    max_humidity_time: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=None, nullable=True)
    min_pressure_time: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=None, nullable=True)
    max_pressure_time: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=None, nullable=True)

    def __repr__(self):
        return f"date: {self.date}, min temperature: {self.min_temperature}, min temperature time: {self.min_temperature_time}, max temperature: {self.max_temperature}, max temperature_time: {self.max_temperature_time}, min humidity: {self.min_humidity}, min humidity time: {self.min_humidity_time}, max humidity: {self.max_humidity}, max humidity time: {self.max_humidity_time}, min pressure: {self.min_pressure}, min pressure time: {self.min_pressure_time}, max pressure: {self.max_pressure}, max pressure time: {self.max_pressure_time}"
