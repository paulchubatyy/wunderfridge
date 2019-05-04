import sys
import logging
import responder
import os
import pickle
from envparse import env
from darksky import forecast
import datetime as dt
import pytz
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


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

GOOGLE_CREDS_STORE = 'data/token.pickle'

api = responder.API(
    debug=DEBUG,
    secret_key=env.str('SECRET_KEY'),
    static_dir='static',
    templates_dir='templates',
    title='WunderFridge'
)

if DEBUG:
    logger.debug("Runinng in debug mode")

local_tz = pytz.timezone(env.str('TIME_ZONE', default='America/Los_Angeles'))
timeformat = env.str('TIME_FORMAT', default='%H:%M')
dateformat = env.str('DATE_FORMAT', default='%a, %b %-d')
datetimeformat = f"{dateformat} {timeformat}"

logger.info(f"local time in {local_tz}: {dt.datetime.now(tz=local_tz)}")

def to_local_datetime(timestamp, tz=None):
    if tz is None:
        timezone = local_tz
    else:
        timezone = pytz.timezone(tz)
    return dt.datetime.fromtimestamp(timestamp, tz=timezone)


def time_format(timestamp, tz=None):
    return to_local_datetime(timestamp, tz).strftime(timeformat)


def date_format(timestamp, tz=None):
    return to_local_datetime(timestamp, tz).strftime(dateformat)


def datetime_format(timestamp, tz=None):
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
    resp.html = api.template('index.html', now=now.strftime('%Y-%m-%dT%H:%M:%SZ'))


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
    resp.html = api.template('weather.html', weather=w, city=city)


@api.route('/wunderlist')
def wunderlist(req, resp):
    todos = []
    resp.html = api.template('wunderlist.html', todos=todos)


@api.route('/calendar')
def calendar(req, resp):
    events_amount = env.int('GOOGLE_CALENDAR_EVENT_COUNT', default=20)
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.isfile(GOOGLE_CREDS_STORE):
        logger.info("Google credentials have been found.")
        with open(GOOGLE_CREDS_STORE, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, fail miserably.
    if not creds:
        logger.error("Failed to deserialize the credentials")
        resp.html = api.template('calendar/error.html')
        return
    if not creds.valid:
        logger.warning("Credentials not valid")
        if not creds.expired or not creds.refresh_token:
            resp.html = api.template('calendar/error.html')
            return
        logger.info("Attempting to renew credentials")
        creds.refresh(Request())
        with open(GOOGLE_CREDS_STORE, 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)

    now = dt.datetime.now(tz=local_tz)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat(),
        maxResults=events_amount,
        singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    resp.html = api.template('calendar/events.html', events=events, now=now)


if __name__ == '__main__':
    api.run()
