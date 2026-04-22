import ast
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel

def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

def get_timezone():
    return current_app.config['TIMEZONE']


db = SQLAlchemy()
migrate = Migrate()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale, timezone_selector=get_timezone)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.sensor import bp as sensor_bp
    app.register_blueprint(sensor_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)

    from app.pwa import bp as pwa_bp
    app.register_blueprint(pwa_bp)

    from app.observations import bp as observations_bp
    app.register_blueprint(observations_bp)

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/meteo.log', maxBytes=10240 * 3, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Meteo startup')
        
    return app

from app import models
