import threading
from flask_celeryext.app import current_celery_app
from flask import copy_current_request_context, request, session, g, jsonify
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


@api.route("/task/<result_id>")
def get_result(result_id):
    # 根据任务ID获取任务结果
    """
    1, 一定要用celery的实例下的AsyncResult获取结果对象，不然获取不到执行结果
    2, result.get() 这个是阻塞方法，还是会导致前端页面卡死
    3, result.result 这个是非阻塞方法，没执行返回None，执行完返回结果
    """
    result = current_celery_app.AsyncResult(id=result_id)
    print(result.status)
    return jsonify(result.result)
