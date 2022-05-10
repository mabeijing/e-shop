import threading

from flask import copy_current_request_context, request, session, g
from tasks.background import async_get_address
from api import api


def send_email():
    import time
    print('sub task start')
    print(request.url)
    print(session.get('user_id'))
    time.sleep(5)
    print('sub task done')
    return 'hello'


@api.route("/task")
def task():
    print(g.name)

    @copy_current_request_context
    def sub_task():
        return send_email()

    task1 = threading.Thread(target=sub_task)
    task1.start()
    # 发送任务到celery,并返回任务ID,后续可以根据此任务ID获取任务结果
    user_id = session.get('user_id')
    result = async_get_address.delay(user_id)
    return result.id

