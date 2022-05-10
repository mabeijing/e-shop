import time
import uuid
import hashlib
from datetime import datetime

from celery import current_app as current_celery_app


def make_celery(_app):
    from flask_celeryext._mapping import FLASK_TO_CELERY_MAPPING
    from flask_celeryext.app import map_invenio_to_celery
    # _celery = Celery(_app.import_name)
    # 注意，这里一定要使用代理对象
    _celery = current_celery_app
    config = map_invenio_to_celery(_app.config, FLASK_TO_CELERY_MAPPING)
    _celery.config_from_object(config)

    class ContextTask(_celery.Task):

        def on_success(self, retval, task_id, args, kwargs):
            print('task done: {0}'.format(retval))
            return super().on_success(retval, task_id, args, kwargs)

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            print('task fail, reason: {0}'.format(exc))
            return super().on_failure(exc, task_id, args, kwargs, einfo)

        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return self.run(*args, **kwargs)

    _celery.Task = ContextTask
    return _celery


def get_now():
    return datetime.now()


def generate_uid():
    return ''.join(str(uuid.uuid4()).split('-'))


def image_md5(file):
    salt = b'rGBIFVBK$%^&'
    md5 = hashlib.md5(salt)
    value = str(file) + str(time.perf_counter_ns())
    md5.update(bytes(value, encoding='utf8'))
    return md5.hexdigest()
