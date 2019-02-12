import os
from envparse import env
from flask import Flask, render_template


env.read_envfile()

# create and configure the app
application = Flask(__name__, instance_relative_config=True)
application.config.from_mapping(
    SECRET_KEY=env.str('SECRET_KEY', default='dev')
)

try:
    os.makedirs(application.instance_path)
except OSError:
    pass

@application.route('/')
def index():
    return render_template('index.html')

import wunderfridge
application.register_blueprint(wunderfridge.bp)

import weather
application.register_blueprint(weather.bp)
