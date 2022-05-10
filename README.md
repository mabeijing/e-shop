学习指南

Flask核心点

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


配置celery
如果写在一个app下，不拆分模块，celery配置非常简单。默认
默认app.py

```python
# app.py
import time
from flask import Flask
from celery import Celery

app = Flask(__name__)

celery_app = Celery(app.name)
celery_app.conf.update(app.config)


@celery_app.task(bind=True)
def async_send_sms(self):
    time.sleep(10)
    return 'success'

@app.route('/task', methods=['POST'])
def task():
    result = async_send_sms.delay()
    return result.id

if __name__ == '__main__':
    app.run()
```
这样，可以基本的flask程序就可以跑起来了。
```shell
# 启动celery任务,
# 进入项目目录，启动任务
# 如果celery的实例对象在模块下[就是.py文件里]。就需要指定模块.实例==app.celery_app
# 如果celery的实例对象在包下[就是__init__.py里]。只需要指定包名==tasks
# 如果在windows下，celery需要增加-P solo。不然启动失败
e-shop> celery -A app.celery_app worker -P solo -E --loglevel=info
# celery -A tasks worker -P solo -E --loglevel=info
```

配置celery定时任务
```python
from celery.schedules import crontab
from datetime import timedelta

# 先配置settings.py
CELERY_BROKER_URL = 'redis://:root123@localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://:root123@localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'  # default json，pickle ，yaml ，msgpack
CELERY_RESULT_SERIALIZER = 'json'
CELERY_WORKER_CONCURRENCY = 20  # 并发数
CELERY_TASK_TIME_LIMIT = 3600  # 秒
CELERY_TIMEZONE = 'Asia/Shanghai'  # celery使用的时区
CELERY_ENABLE_UTC = True  # 启动时区设置
CELERY_WORKER_LOG_COLOR = True
CELERY_IMPORTS = (  # 这里配置celery发现任务的模块
    "tasks.scheduler",
    "tasks.background"
)
# 定时任务配置
# tasks: {  这里名字随意
#   'task':  'tasks.scheduler.send_sms' 这里必须绝对导入路径。
CELERY_BEAT_SCHEDULE = {
    'tasks': {
        'task': 'tasks.scheduler.send_sms',
        'schedule': crontab(minute="*/1"),
        # 'schedule': timedelta(seconds=10),
        'args': ()
    }
}
```
```python
# tasks.__init__.py 这里就是celery的实例对象，可以用-A tasks启动。
from app import ext

celery = ext.celery
```
```python
# tasks.scheduler.py
from tasks import celery

@celery.task
def send_sms():
    return 'success'
```
```python
# app.py
from flask_celeryext import FlaskCeleryExt
from flask import Flask

app = Flask(__name__)
ext = FlaskCeleryExt(app)

# 这里注意。不能直接从task导入send_sms，会导致循环导入。
# from tasks.scheduler import send_sms
# 但是可以放在视图函数内使用

@app.route('/task', methods=['POST'])
def task():
    from tasks.scheduler import send_sms
    result = send_sms.delay()
    return result.id
```

```shell
# 启动定时任务
e-shop> celery -A tasks beat --loglevel=info
```


安装
Flask，
Flask-sqlalchemy
Flask-CeleryExt
sqlalchemy
pymysql
redis
celery
