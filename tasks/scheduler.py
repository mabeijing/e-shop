from . import celery_logger
from celery import current_app as celery


@celery.task(name='tasks.scheduler.send_sms')
def send_sms():
    """
    print('准备发送短信')
    [2022-05-12 12:55:00,058: WARNING/MainProcess] 准备发送短信
    [2022-05-12 12:55:00,058: ERROR/MainProcess] tasks.scheduler.send_sms[c2014588-f769-4215-85f8]: 短信发送中...
    print是不带任务名和id的，不推荐使用
    """
    celery_logger.error('短信发送中...')
    return '发送成功'
