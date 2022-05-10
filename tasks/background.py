from . import celery
from celery.utils.log import get_task_logger
from models import *

celery_logger = get_task_logger(__name__)


@celery.task(name='tasks.background.async_get_address', bind=True, serializer='json')
def async_get_address(self, user_id):
    self.update_state(state="PROGRESS", meta={'progress': 10})
    celery_logger.error('this is error log.')
    time.sleep(10)
    self.update_state(state="PROGRESS", meta={'progress': 50})
    user = User.query.filter_by(user_id=user_id).first()
    address_list = user.address.filter_by(user_id=user_id).all()
    time.sleep(10)
    self.update_state(state="PROGRESS", meta={'progress': 100})
    return [address.serialize() for address in address_list]
