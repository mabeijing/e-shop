from celery import Celery


def make_celery(_app):
    from flask_celeryext._mapping import FLASK_TO_CELERY_MAPPING
    from flask_celeryext.app import map_invenio_to_celery
    _celery = Celery(_app.import_name)
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
