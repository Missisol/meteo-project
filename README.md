## Регистрация метеоданных (температура, влажность, давление) от датчиков DHT22 и BME280 с использованием ESP8266 и Raspberry Pi

***[Project on Github](https://github.com/Missisol/meteoProject/tree/develop)***

***[Sketches on Github](https://github.com/Missisol/ESP8266_BME280_DHT22_project)*** - скетчи для ESP8266 с BME280 и DHT22

---

### Настройка проекта
- Создание виртуальной среды - `python3 -m venv <env name>`
- Активация витруальной среды - `source <env name>/bin/activate`
- Установка зависимостей - `pip install -r requirements.txt`
- Если файервол (UFW) включен, должен быть открыт доступ к портам, на которых будет открываться проект, и к порту 1883

#### Mosquitto MQTT Broker
- Mожно использовать Mosquitto Brocker, установленный на Raspberry Pi:    
    - установка Mosquitto Broker на Raspberry Pi
    `sudo apt install -y mosquitto mosquitto-clients`
    - настройка автоматического запуска Mosquitto Broker при загрузке RPI - `sudo systemctl enable mosquitto.service`
    - для удаленного доступа без аутентификации в конфигурационный файл /etc/mosquitto/mosquitto.conf добавить:  
        `listener 1883`  
        `allow_anonymous true`
- Можно использовать Mosquitto Brocker в докер-контейнере:
    - создать файл mosquitto.conf в домашней директории
    - запустить Mosquitto Broker в контейнере  - `docker run -d --restart always --name <name> -p 1883:1883 -v $HOME/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto:2`

#### Расписание задач с Cron
- Настройка расписания выполнения задач с использованием Cron 
    - `crontab -e`
    - `* * * * * cd <path_to_project_directory> && <env name>/bin/flask <command_name>`
- когда проет запущен, в терминале запускаем команду - `(.venv) $  flask --help`. В разделе Commands видим команду (в данном проекте - `scheduled Cron job`)
- когда проет запущен, в терминале запускаем команду - в данном проекте - `(.venv) $  flask scheduled`. В разделе Commands видим перечень задач

---

### Запуск проекта
#### Разработка
- Запуск проекта в dev режиме - `flask run --host=0.0.0.0`

#### Деплой
- установить supervisor - `sudo apt install supervisor`
- создать файл конфигурации supervisor /etc/supervisor/conf.d/meteo.conf  
&nbsp;&nbsp;&nbsp;&nbsp;`[program:meteo]`  
&nbsp;&nbsp;&nbsp;&nbsp;`command=/<path-to-project>/.venv/bin/gunicorn -k gevent -b 0.0.0.0:8000 meteo:app`  
&nbsp;&nbsp;&nbsp;&nbsp;`directory=/<path-to-project>`  
&nbsp;&nbsp;&nbsp;&nbsp;`user=<username>`  
&nbsp;&nbsp;&nbsp;&nbsp;`autostart=true`  
&nbsp;&nbsp;&nbsp;&nbsp;`autorestart=true`  
&nbsp;&nbsp;&nbsp;&nbsp;`stopasgroup=true`  
&nbsp;&nbsp;&nbsp;&nbsp;`killasgroup=true` 
- команды: `sudo supervisorctl reload`, `sudo supervisorctl start/stop meteo`

#### Деплой в докер-контейнере
- остановить Mosquitto Broker, если он уже запущен на RPI или в докер-контейнере
- `docker compose up`

---

#### Команды
- Command for working with the database entities without having to import them `flask shell`
- `flask db downgrade base` - when the downgrade command is not given a target, it downgrades one revision. The base target causes all migrations to be downgraded, until the database is left at its initial state, with no tables.
- Create requirements file - `pip freeze > requirements.txt`

---

#### Ссылки
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- [ESP8266 Publishing DHT22 Readings with MQTT to Raspberry Pi](https://randomnerdtutorials.com/esp8266-publishing-dht22-readings-with-mqtt-to-raspberry-pi/)
- [Mosquitto Brocker settings](https://randomnerdtutorials.com/how-to-install-mosquitto-broker-on-raspberry-pi/)
- [How to Configure Mosquitto MQTT Broker in Docker](https://cedalo.com/blog/mosquitto-docker-configuration-ultimate-guide/)
- [Setting Up Gunicorn and Supervisor](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux)
- [Flask regularly scheduled jobs with Cron](https://blog.miguelgrinberg.com/post/run-your-flask-regularly-scheduled-jobs-with-cron)
- [crontab guru](https://crontab.guru/)
-  cron need not be restarted whenever a crontab file is modified - [man cron](https://www.manpagez.com/man/8/cron/), but `sudo service cron reload`

