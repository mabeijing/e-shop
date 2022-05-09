from flask import Flask, session, request, jsonify
from settings import DEV
from models import *
from werkzeug.utils import secure_filename
import os
from celery import Celery
from celery.utils.log import get_task_logger

app = Flask(__name__, static_folder='static')
app.config.from_object(DEV)
db.init_app(app)

celery_logger = get_task_logger(__name__)


def make_celery(app):
    _celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )

    _celery.conf.update(app.config)

    class ContextTask(_celery.Task):

        def on_success(self, retval, task_id, args, kwargs):
            print('task done: {0}'.format(retval))
            return super().on_success(retval, task_id, args, kwargs)

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            print('task fail, reason: {0}'.format(exc))
            return super().on_failure(exc, task_id, args, kwargs, einfo)

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    _celery.Task = ContextTask
    return _celery


# celery_app = Celery(app.name, broker='redis://:root123@localhost:6379/0', backend='redis://:root123@localhost:6379/0')

celery_app = make_celery(app)


# with app.app_context():
#     db.init_app(app)
#     db.create_all()
@celery_app.task(name='app.send_sms')
def send_sms():
    time.sleep(10)
    print('123456')
    celery_logger.error('csdcasdcasodicasodicjosidcjasodi')
    return '发送成功'


@celery_app.task(name='app.my_background_task', bind=True, serializer='json')
def my_background_task(self, user_id):
    # print(dir(self))
    self.update_state(state="PROGRESS", meta={'progress': 10})
    celery_logger.error('this is error log.')
    time.sleep(10)
    self.update_state(state="PROGRESS", meta={'progress': 50})
    user = User.query.filter_by(user_id=user_id).first()
    address_list = user.address.filter_by(user_id=user_id).all()
    time.sleep(10)
    self.update_state(state="PROGRESS", meta={'progress': 100})
    return [address.serialize() for address in address_list]


@app.route("/task")
def task():
    # 发送任务到celery,并返回任务ID,后续可以根据此任务ID获取任务结果
    user_id = session.get('user_id')
    result = my_background_task.delay(user_id)
    return result.id


@app.route("/task/<result_id>")
def get_result(result_id):
    # 根据任务ID获取任务结果
    """
    1, 一定要用celery的实例下的AsyncResult获取结果对象，不然获取不到执行结果
    2, result.get() 这个是阻塞方法，还是会导致前端页面卡死
    3, result.result 这个是非阻塞方法，没执行返回None，执行完返回结果
    """
    result = celery_app.AsyncResult(id=result_id)
    print(result.status)
    return jsonify(result.result)


@app.before_request
def is_login():
    white_list = ['/login', '/register']
    if request.method == 'POST' and request.path in white_list:
        return
    if not session.get('user_id'):
        return {'code': 40014, 'msg': '用户未登录'}


@app.route('/register', methods=['POST'])
def register():
    account = request.form.get('account')
    data = {
        'account': account,
        'password': request.form.get('password'),
        'nick_name': request.form.get('nick_name'),
        'age': request.form.get('age'),
        'avatar': request.form.get('avatar'),
        'id_card': request.form.get('id_card'),
        'gender': request.form.get('gender'),
        'balance': request.form.get('balance')
    }

    if User.query.filter_by(account=account).first():
        return {'code': 40010, 'msg': '用户已存在'}
    user = User(**data)
    user.save()
    return user.serialize()


@app.route('/login', methods=['POST'])
def login():
    account = request.form.get('account')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')
    user = User.query.filter_by(account=account).first()
    if not user:
        return {'code': 40017, 'msg': '用户未注册'}
    if user.check_password(password):
        user.login_time = get_now()
        user.save()
        session['user_id'] = user.user_id
        if remember_me:
            session.permanent = True
    else:
        return {'code': 40016, 'msg': '用户名或密码不正确'}
    return user.serialize()


# string 不含/的任何字符
@app.route('/detail/<string:account>', methods=['POST'])
def detail(account):
    user = User.query.filter_by(account=account).first()
    if not user:
        return {'code': 40015, 'msg': f'{account}用户不存在'}
    else:
        if session.get('user_id') != user.user_id:
            return {'code': 40019, 'msg': '无权限操作他人用户'}
    print(user.vip)
    return user.serialize()


@app.route('/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    user.logout_time = get_now()
    user.save()
    session.clear()
    return {'code': 40018, 'msg': f'{user.account}退出成功'}


# build_in converter [string, int, float, path, uuid] default string
@app.route('/delete/<string:account>', methods=['POST'])
def delete_account(account):
    user = User.query.filter_by(account=account).first()
    user_id = session.get('user_id')
    admin = User.query.filter_by(user_id=user_id).first()
    if admin.account == 'beijingm':
        if not user:
            return {'code': 40017, 'msg': f'{account}不存在'}
        user.delete()
        return {'code': 40020, 'msg': f'{account}删除成功'}
    else:
        return {'code': 40019, 'msg': '非管理员权限无法操作'}


@app.route('/address/list', methods=['POST'])
def get_address():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    address_list = user.address.filter_by(user_id=user_id).all()
    return jsonify([address.serialize() for address in address_list])


@app.route('/address/add', methods=['POST'])
def add_address():
    data = {
        'province': request.form.get('province'),
        'city': request.form.get('city'),
        'county': request.form.get('county'),
        'user_id': session.get('user_id'),
    }
    address = Address(**data)
    address.save()
    return address.serialize()


@app.route('/address/<int:address_id>', methods=['POST'])
def edit_address(address_id: int):
    user_id = session.get('user_id')
    form = request.form.to_dict()
    form['detail'] = form['province'] + form['city'] + form['county']
    # form['UPDATE_TIME'] = get_now()
    user = User.query.filter_by(user_id=user_id).first()
    try:
        user.address.filter_by(id=address_id).update(form)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    address = user.address.filter_by(id=address_id).first()
    return address.serialize()


@app.route('/address/delete/<int:address_id>', methods=['POST'])
def delete_address(address_id: int):
    address = Address.query.filter_by(id=address_id).first()
    if not address:
        return {'code': 40404, 'msg': '删除失败'}
    address.delete()
    return {'code': 40404, 'msg': '删除成功'}


@app.route('/api/goods/type/add', methods=['POST'])
def add_good_type():
    name = request.form.get('name')
    good = GoodType(name=name)
    good.save()
    return good.serialize()


@app.route('/api/goods/type/delete', methods=['DELETE'])
def delete_good_type():
    _id = request.form.get('id')
    good = GoodType.query.filter_by(id=_id).first()
    if not good:
        return {'code': 40019, 'msg': '商品id不存在'}
    good.delete()
    return {'code': 200, 'msg': '删除成功'}


@app.route('/api/goods/type', methods=['POST'])
def good_type():
    good_list = GoodType.query.all()
    goods = [good.serialize() for good in good_list] if good_list else []
    return jsonify(goods)


@app.route('/api/goods/add', methods=['POST'])
def add_good():
    avatar = request.files.get('avatar')
    if not avatar:
        file_path = ''
    else:
        file_path = f'static/uploads/{image_md5(secure_filename(avatar.filename))}.jpeg'
        avatar.save(file_path)
    data = {
        'good_name': request.form.get('good_name'),
        'good_type_id': request.form.get('good_type_id'),
        'origin_price': request.form.get('origin_price'),
        'sell_price': request.form.get('sell_price'),
        'contains': request.form.get('contains'),
        'produce_time': request.form.get('produce_time'),
        'image': file_path
    }
    good = Goods(**data)
    good.save()

    return good.serialize()


@app.route('/api/goods', methods=['POST', 'GET'])
def goods():
    if request.method == 'GET':
        count = Goods.query.count()
        return {'code': 40044, 'msg': count}
    if request.method == 'POST':
        _page = request.form.get('page')
        _page_size = request.form.get('page_size')
        page = int(_page) if _page else None
        page_size = int(_page_size) if _page_size else None
        paginate = Goods.query.paginate(page=page, per_page=page_size, error_out=False)
        goods_list = [i.serialize() for i in paginate.items]
        data = {
            'total': paginate.total,
            'pages': paginate.pages,
            'goods_num': len(goods_list),
            'goods': goods_list
        }
        return jsonify(data)


@app.route('/api/goods/delete', methods=['DELETE'])
def good_delete():
    _id = request.form.get('id')
    good = Goods.query.filter_by(id=_id).first()
    if not good:
        return {'code': 40444, 'msg': '查询的货物不存在'}
    image = good.image
    good_name = good.good_name
    good.delete()
    if image:
        os.remove(path=image)
    return {'code': 40044, 'msg': f'[{good_name}]删除成功'}


@app.route('/vip/register', methods=['POST'])
def add_vip():
    user_id = session.get('user_id')
    data = {
        'name': request.form.get('name'),
        'level': request.form.get('level'),
        'user_id': user_id
    }
    vip = Vip(**data)
    vip.save()
    return vip.serialize()


@app.errorhandler(SQLAlchemyError)
def error_handle(e):
    print(e)
    return {'code': 50010, 'msg': '数据库错误'}


@app.errorhandler(404)
def error_handle(e):
    return {'code': e.code, 'msg': e.description}, 404


@app.errorhandler(405)
def error_handle(e):
    return {'code': e.code, 'msg': e.description}, 405


if __name__ == '__main__':
    app.run()
