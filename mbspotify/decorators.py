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


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    # Based on snippet from http://flask.pocoo.org/snippets/79/.
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function
