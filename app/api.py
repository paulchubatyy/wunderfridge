import responder
from envparse import env
from darksky import forecast
import datetime as dt
import pytz


env.read_envfile()

api = responder.API(
    debug=env.bool('DEBUG', default=False),
    secret_key=env.str('SECRET_KEY')
)

local_tz = pytz.timezone(env.str('TIME_ZONE', default='America/Los_Angeles'))
timeformat = env.str('TIME_FORMAT', default='%H:%M')
dateformat = env.str('DATE_FORMAT', default='%a, %b %-d')
datetimeformat = f"{dateformat} {timeformat}"

def to_local_datetime(timestamp, tz):
    timezone = pytz.timezone(tz)
    return dt.datetime.fromtimestamp(timestamp, tz=timezone)


def time_format(timestamp, tz):
    return to_local_datetime(timestamp, tz).strftime(timeformat)


def date_format(timestamp, tz):
    return to_local_datetime(timestamp, tz).strftime(dateformat)


def datetime_format(timestamp, tz):
    return to_local_datetime(timestamp, tz).strftime(datetimeformat)


api.jinja_env.filters['timefilter'] = time_format
api.jinja_env.filters['datefilter'] = date_format
api.jinja_env.filters['datetimefilter'] = datetime_format


weather_units = env.str('DARKSKY_UNITS', default=None)


def temperature_format(temp):
    units = 'C' if weather_units == 'si' else 'F'
    return f"{int(temp)}°{units}"


api.jinja_env.filters['temperaturefilter'] = temperature_format



@api.route('/')
def index(req, resp):
    now = dt.datetime.now(tz=local_tz)
    resp.text = api.template('index.html', now=now.strftime('%Y-%m-%dT%H:%M:%SZ'))


@api.route('/healthcheck')
def healthcheck(req, resp):
    resp.text = "all good"


@api.route('/weather')
def weather(req, resp):
    location = env('DARKSKY_COORDINATES', postprocessor=lambda x: x.split(';'))
    lang = env.str('DARKSKY_LANG', default=None)
    city = env.str('WEATHER_LOCATION', default='San Jose')
    data = {}
    w = forecast(
        env.str('DARKSKY_KEY'), *location, units=weather_units, lang=lang)
    resp.text = api.template(
        'weather.html', weather=w, city=city)


@api.route('/wunderlist')
def wunderlist(req, resp):
    todos = []
    resp.text = api.template('wunderlist.html', todos=todos)


if __name__ == '__main__':
    api.run()