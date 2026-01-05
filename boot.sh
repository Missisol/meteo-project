#!/bin/bash
export APP_ENV=production
flask db upgrade
exec gunicorn -k gevent -b 0.0.0.0:5022 --access-logfile - --error-logfile - meteo:app