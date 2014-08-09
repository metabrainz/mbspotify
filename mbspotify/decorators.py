from functools import wraps
from flask import current_app, request
from werkzeug.exceptions import BadRequest


def key_required(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if request.args.get('key') not in current_app.config['ACCESS_KEYS']:
            raise BadRequest("You need to provide a key.")
        return f(*args, **kwds)

    return wrapper
