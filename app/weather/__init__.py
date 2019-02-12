from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import simplejson as json
from pyowm import OWM
from envparse import env


bp = Blueprint('weather', __name__, template_folder='templates')

owm = OWM(env.str('OWM_KEY'))
obs = owm.weather_at_id(env.int('OWM_LOCATION_ID', default=5392171))

@bp.route('/current')
def current():
    weather = obs.get_weather()
    location = obs.get_location()
    temp_units = env.str('OWM_TEMP_UNITS')
    data = dict(
        location_name=location.get_name(),
        temperature=weather.get_temperature(temp_units),
        clouds = weather.get_clouds(),
        temp_units=temp_units
    )
    return render_template('current.html', **data)
