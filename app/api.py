import responder
from envparse import env
from darksky import forecast
import datetime as dt
import pytz


def format_datetime(value, format='medium'):
    if format == 'full':
        format = "EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format = "EE dd.MM.y HH:mm"
    return babel.dates.format_datetime(value, format)


api.jinja_env.filters['datetime'] = format_datetime

api = responder.API()
env.read_envfile()


@api.route('/')
def index(req, resp):
    resp.text = api.template('index.html')


@api.route('/weather')
def weather(req, resp):
    location = env('DARKSKY_COORDINATES', postprocessor=lambda x: x.split(';'))
    units = env.str('DARKSKY_UNITS', default=None)
    celsius = True if units == 'si' else False
    lang = env.str('DARKSKY_LANG', default=None)
    city = env.str('WEATHER_LOCATION', default='San Jose')
    data = {}
    with forecast(env.str('DARKSKY_KEY'), *location,
                  units=units, lang=lang) as weather:
        resp.text = api.template(
            'weather.html', weather=weather, city=city, celsius=celsius)


if __name__ == '__main__':
    api.run(debug=env.bool('DEBUG', default=False))