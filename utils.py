import time
import uuid
import hashlib
from datetime import datetime, date
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps

from flask.json import JSONEncoder
from flask import session

from exceptions import UserAccessNotAuthorized

cache = Cache()

limit = Limiter(key_func=get_remote_address)


def is_administrator(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        if session.get('role_id') != 1:
            raise UserAccessNotAuthorized()
        return fun(*args, **kwargs)

    return wrapper


class FlaskJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return JSONEncoder.default(self, obj)


def get_now():
    return datetime.now()


def generate_uid():
    return ''.join(str(uuid.uuid4()).split('-'))


def image_md5(file):
    salt = b'5678654567%^&'
    md5 = hashlib.md5(salt)
    value = str(file) + str(time.perf_counter_ns())
    md5.update(bytes(value, encoding='utf8'))
    return md5.hexdigest()
