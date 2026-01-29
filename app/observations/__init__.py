from flask import Blueprint

bp = Blueprint('observations', __name__)

from app.observations import routes