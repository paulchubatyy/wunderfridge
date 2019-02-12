from functools import wraps
from flask import Response
import simplejson as json


def jsonify(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        return Response(json.dumps(view(*args, **kwargs)), mimetype='application/json')
    return wrapped
