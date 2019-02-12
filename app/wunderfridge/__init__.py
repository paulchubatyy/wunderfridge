import time

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import simplejson as json
from .decorators import jsonify

bp = Blueprint('wunderfridge', __name__, template_folder='templates',
                static_folder='static')


def current_timestamp(): return int(round(time.time() * 1000))


@bp.route('/localtime')
@jsonify
def localtime():
    return {'datetime': current_timestamp() }
