#   项目指南


### Flask

1，wsgi协议

2，2个本地栈。LocalStack ==> _request_ctx_stack, _app_ctx_stack

3，2个上下文。AppContext, RequestContext

4，4个代理对象。current_app, g, request, session

5，Jinja2模板


Flask重要概念：
*   Flask是符合wsgi协议的应用，即wsgi服务器收到请求后，会执行应用app(environ, tart_response)。也就是说Flask必须实现__call__， 
    environ是wsgi服务器传递过来包含所有请求参数的一个字典，tart_response是wsgi接收的回调函数。都是固定参数。
    
*   flask执行call方法后，会ctx = self.request_context(environ)创建一个请求上下文，ctx.push()。
    先给request赋值
    然后将应用上下文入栈。app_ctx = self.app.app_context()创建一个应用上下文，app_ctx.push()入栈。
    最后给session赋值

*   在RequestContext和AppContext都入栈后，代理对象就可以访问了。 
    request代理，其实就是RequestContext.request。必须拿到请求environ才有值。
    session代理，其实就是RequestContext.session。值保存在浏览器或者redis，所以可以跨请求获取。
    current_app就是栈顶flask的实例对象。
    g是应用上下文的一个属性读取器。每次请求都不一样。生命周期一次请求。
    作用域都是当前请求线程内。无法跨线程访问。生命周期是请求入栈到出栈。
    

代理对象必须在入栈后才能使用
应用上下文可以通过flask实例app.app_context()创建一个应用上下文。获取代码逻辑，自己的代码都可以在应用上下文种执行。
请求上下文比较难构造。app.app.test_request_context()必须传入值才能得到有效上下文。


### celery
celery本身功能很复杂。感觉和flask差不多，都有核心对象，代理对象，配置文件，装饰器，用法很像。
```python
import flask
from celery import Celery

app = Celery(__name__)
app.config_from_object(flask.Config)

@app.task
def task():
    ...

```
和flask是可以分离的，flask_celery只是简单做了和flask配置的共享。完全可以单独配置。
celery是支持分布式的，只要task代码一样，配置一样，中间件一样。理论上可执行（未验证）。
```python
# from flask_celeryext._mapping import FLASK_TO_CELERY_MAPPING 做了celery配置和flask的映射关系
from celery.schedules import crontab
CELERY_BROKER_URL = 'redis://:root123@localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://:root123@localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'  # default json，pickle ，yaml ，msgpack
CELERY_RESULT_SERIALIZER = 'json'
CELERY_WORKER_CONCURRENCY = 20  # 并发数
CELERY_TASK_TIME_LIMIT = 3600  # 秒
CELERY_TIMEZONE = 'Asia/Shanghai'  # celery使用的时区
CELERY_ENABLE_UTC = True  # 启动时区设置
CELERY_WORKER_LOG_COLOR = True

# celery发现task目录，很关键
CELERY_IMPORTS = (
    "tasks.scheduler",
    "tasks.background"
)
# celery定时任务配置，也很关键
CELERY_BEAT_SCHEDULE = {
    'tasks': {
        'task': 'tasks.scheduler.send_sms',
        'schedule': crontab(minute="*/1"),
        'args': ()
    }
}
```

```python
# 第一种用法，不拆分模块
# app.py
from flask import Flask
from flask_celeryext import FlaskCeleryExt

app = Flask(__name__)
ext = FlaskCeleryExt(app)
celery = ext.celery

@celery.task(bind=True)
def task(self):
    ...

@app.route('/index')
def index():
    future = task.delay()
    return future.id

if __name__ == '__main__':
    app.run()
```

```python
# 第二种用法，拆分tasks。独立tasks包
# tasks包下使用
# __init__.py
# 如需要自定义make_celery，请参考下方法
from flask_celeryext._mapping import FLASK_TO_CELERY_MAPPING
from flask_celeryext.app import map_invenio_to_celery
from flask_celeryext import FlaskCeleryExt
from celery import current_app as current_celery_app
from celery.utils.log import get_task_logger

celery_logger = get_task_logger(__name__)


def _make_celery(_app):
    # _celery = Celery(_app.import_name)
    # 注意，这里一定要使用代理对象
    _celery = current_celery_app
    config = map_invenio_to_celery(_app.config, FLASK_TO_CELERY_MAPPING)
    _celery.config_from_object(config)

    class ContextTask(_celery.Task):

        def on_success(self, retval, task_id, args, kwargs):
            print('task done: {0}'.format(retval))
            return super().on_success(retval, task_id, args, kwargs)

        def on_failure(self, exc, task_id, args, kwargs, e_info):
            print('task fail, reason: {0}'.format(exc))
            return super().on_failure(exc, task_id, args, kwargs, e_info)

        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return self.run(*args, **kwargs)

    _celery.Task = ContextTask
    return _celery


ext = FlaskCeleryExt(create_celery_app=_make_celery)

```
```python
# app.py
# 完成celery绑定flask对象
from flask import Flask

from tasks import ext
app = Flask(__name__)
ext.init_app(app)
celery = ext.celery
```

```python
# tasks包下使用
# background.py
# 实际异步任务
from celery import current_app as celery


@celery.task(name='tasks.scheduler.send_sms')   # name一定是从包开始导入
def send_sms():
    ...
    return '发送成功'
```
```python
# 最后，就可以在blueprint下使用
from flask_celeryext.app import current_celery_app
from flask import session, jsonify
from tasks.background import async_get_address
from api import api

@api.route("/task")
def task():
    user_id = session.get('user_id')
    result = async_get_address.delay(user_id)
    return result.id


@api.route("/task/<result_id>")
def get_result(result_id):
    result = current_celery_app.AsyncResult(id=result_id)
    print(result.status)
    return jsonify(result.result)
```


```shell
# 启动celery worker
e-shop> celery -A app.celery worker -P solo -E --loglevel=info

 -------------- celery@LAPTOP-Ducker v5.2.6 (dawn-chorus)
--- ***** -----
-- ******* ---- Windows-10-10.0.22000-SP0 2022-05-12 12:49:54
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         default:0x1eeaae7a3a0 (.default.Loader)
- ** ---------- .> transport:   redis://:**@localhost:6379/0
- ** ---------- .> results:     redis://:**@localhost:6379/0
- *** --- * --- .> concurrency: 20 (solo)
-- ******* ---- .> task events: ON
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery


[tasks]
  . tasks.background.async_get_address
  . tasks.scheduler.send_sms
# 这样就算启动成功

# 启动celery定时任务
e-shop> celery -A app.celery beat --loglevel=info
celery beat v5.2.6 (dawn-chorus) is starting.
__    -    ... __   -        _
LocalTime -> 2022-05-12 12:50:52
Configuration ->
    . broker -> redis://:**@localhost:6379/0
    . loader -> celery.loaders.default.Loader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule
    . logfile -> [stderr]@%INFO
    . maxinterval -> 5.00 minutes (300s)
[2022-05-12 12:50:52,146: INFO/MainProcess
```

### orm数据库

### socketIO

### form表单验证

### exceptions

### grpc

### uwsgi

### nginx

### docker

### marshmallow


### 数据表设计

```