from functools import wraps
from flask import current_app, request
from werkzeug.exceptions import BadRequest


def key_required(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if current_app.config['KEY'] != request.args.get('key'):
            raise BadRequest("You need to provide a key.")
        return f(*args, **kwds)

    return wrapper
