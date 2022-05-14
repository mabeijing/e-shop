from urllib.parse import quote_plus
from datetime import timedelta

import redis
from celery.schedules import crontab

# 连接数据库

# 增加对数据库密码特殊字符的兼容
conf = {'username': 'root',
        'password': quote_plus('Root123!'),
        'host': 'localhost',
        'port': 3306,
        'database': 'e-shop'}


# 支持多数据库配置


class DEV:
    DEBUG = True
    SECRET_KEY = '123'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'.format(**conf)
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # 动态追踪sql
    SQLALCHEMY_ECHO = False  # 显示sql
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    JSON_AS_ASCII = False  # 开启中文

    SESSION_TYPE = 'redis'
    SESSION_KEY_PREFIX = "session:"
    SESSION_REDIS = redis.Redis(host='127.0.0.1', port='6379', password='root123')

    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_PASSWORD = 'root123'
    CACHE_REDIS_DB = 10
    CACHE_KEY_PREFIX = 'cache_endpoint_'

    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET_KEY = '123qwe'
    WTF_I18N_ENABLED = False  # 如果使用flask_wtf，就需要关闭wtforms使用flask的

    # redis://:password@hostname:port/db_number
    CELERY_BROKER_URL = 'redis://:root123@localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://:root123@localhost:6379/0'
    CELERY_TASK_SERIALIZER = 'json'  # default json，pickle ，yaml ，msgpack
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_WORKER_CONCURRENCY = 20  # 并发数
    CELERY_TASK_TIME_LIMIT = 3600  # 秒
    CELERY_TIMEZONE = 'Asia/Shanghai'  # celery使用的时区
    CELERY_ENABLE_UTC = True  # 启动时区设置
    CELERY_WORKER_LOG_COLOR = True
    CELERY_IMPORTS = (
        "tasks.scheduler",
        "tasks.background"
    )
    # celery beat
    CELERY_BEAT_SCHEDULE = {
        'tasks': {
            'task': 'tasks.scheduler.send_sms',
            'schedule': crontab(minute="*/1"),
            # 'schedule': timedelta(seconds=10),
            'args': ()
        }
    }
