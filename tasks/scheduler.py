import time

from . import celery


@celery.task(name='tasks.scheduler.send_sms')
def send_sms():
    time.sleep(10)
    print('准备发送短信')
    return '发送成功'
