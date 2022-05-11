from flask import Flask, session, request, jsonify, g
from flask_celeryext import FlaskCeleryExt
from settings import DEV
from models import *
from utils import make_celery, get_now
from sqlalchemy.exc import SQLAlchemyError
from api import api
from exceptions import *

app = Flask(__name__, static_folder='static')
app.config.from_object(DEV)
db.init_app(app)
app.register_blueprint(api)
ext = FlaskCeleryExt(create_celery_app=make_celery)
ext.init_app(app)


# with app.app_context():
#     db.init_app(app)
#     db.create_all()

# @app.route("/task/<result_id>")
# def get_result(result_id):
#     result = ext.celery.AsyncResult(id=result_id)
#     return jsonify(result.result)

@app.before_request
def is_login():
    g.name = 'before request~~~'
    white_list = ['/api/user/login', '/api/user/register']
    if request.method == 'POST' and request.path in white_list:
        return
    if not session.get('user_id'):
        raise UserNotLogin()


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
    goods_li = [good.serialize() for good in good_list] if good_list else []
    return jsonify(goods_li)


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


@app.errorhandler(Exception)
def error_handle(e: Exception):
    if isinstance(e, BasicException):
        return e.serialize()


if __name__ == '__main__':
    app.run()
