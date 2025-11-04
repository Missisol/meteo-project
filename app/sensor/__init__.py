from flask import Blueprint

bp = Blueprint('sensor', __name__)

from app.sensor import routes