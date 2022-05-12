import time

from celery import current_app as celery

from models import *


@celery.task(name='tasks.background.async_get_address', bind=True, serializer='json')
def async_get_address(self, user_id):
    """
    通过给task(bind=True)，让被装饰task第一个参数接收self，就是task本身。
    通过指定serializer序列化返回值
    self的自身状态有几种。PROGRESS， INIT, FAIL, SUCCESS，其中PROGRESS就是执行中，可以插入meta=dict来增加进度，状态之类。
    通过celery.AsyncResult.result就可以拿到执行结果，或者status.meta的属性。
    """
    self.update_state(state="PROGRESS", meta={'progress': 10})
    time.sleep(5)
    self.update_state(state="PROGRESS", meta={'progress': 50})
    user = User.query.filter_by(user_id=user_id).first()
    address_list = user.address.filter_by(user_id=user_id).all()
    time.sleep(5)
    self.update_state(state="PROGRESS", meta={'progress': 100})
    return [address.serialize() for address in address_list]
