import sys
import logging
import responder
from envparse import env
from darksky import forecast
import datetime as dt
import pytz


env.read_envfile()

DEBUG=env.bool('DEBUG', default=False),

logger = logging.getLogger('__name__')
formatter = logging.Formatter('%(levelname)s: %(message)s')
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
h1 = logging.StreamHandler(sys.stdout)
h1.setFormatter(formatter)
if DEBUG:
    h1.setLevel(logging.DEBUG)
else:
    h1.setLevel(logging.INFO)
h1.addFilter(lambda record: record.levelno <= logging.INFO)
h2 = logging.StreamHandler()
h2.setFormatter(formatter)
h2.setLevel(logging.WARNING)
logger.addHandler(h1)
logger.addHandler(h2)

api = responder.API(
    debug=DEBUG,
    secret_key=env.str('SECRET_KEY')
)

if DEBUG:
    logger.debug("Runinng in debug mode")

local_tz = pytz.timezone(env.str('TIME_ZONE', default='America/Los_Angeles'))
timeformat = env.str('TIME_FORMAT', default='%H:%M')
dateformat = env.str('DATE_FORMAT', default='%a, %b %-d')
datetimeformat = f"{dateformat} {timeformat}"

logger.info(f"local time in {local_tz}: {dt.datetime.now(tz=local_tz)}")

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

logger.info("Added jinja filters")


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

@api.route('/calendar')
def calendar(req, resp):
    pass


if __name__ == '__main__':
    api.run()
