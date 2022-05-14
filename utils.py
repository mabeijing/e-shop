import time
import uuid
import hashlib
from datetime import datetime
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

cache = Cache()

limit = Limiter(key_func=get_remote_address)


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
