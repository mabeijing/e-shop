from flask import request, session, jsonify, url_for
from exceptions import *
from . import api
from models import *
from utils import get_now, cache, limit


@api.route('/user/register', methods=['POST'])
def user_register():
    account = request.form.get('account')
    admin = request.form.get('administrator')
    flag = False
    if str(admin) and (str(admin) == 'true' or str(admin) == 'True' or str(admin) == '1'):
        flag = True
    data = {
        'account': account,
        'password': request.form.get('password'),
        'nick_name': request.form.get('nick_name'),
        'age': request.form.get('age'),
        'avatar': request.form.get('avatar'),
        'id_card': request.form.get('id_card'),
        'gender': request.form.get('gender'),
        'balance': request.form.get('balance'),
        'administrator': flag
    }

    if User.query.filter_by(account=account).first():
        raise UserAlreadyExists()
    user = User(**data)
    user.save()
    return user.serialize()


# string 不含/的任何字符
@api.route('/user/<string:account>', methods=['POST'])
def user_detail(account):
    if not session['is_admin']:
        raise UserAccessNotAuthorized()
    user = User.query.filter_by(account=account).first()
    if not user:
        raise UserNotFound(message=f'{account}用户不存在')
    print(user.vip)
    return user.serialize()


@api.route('/users', methods=['GET', 'POST'])
def user_list():
    user_id = session.get('user_id')
    admin = User.query.filter_by(user_id=user_id).first()
    if not admin:
        raise UserNotLogin()
    users = [u.serialize() for u in User.query.filter_by().all() if u]
    return jsonify(users)


@api.route('/user/<string:account>', methods=['PUT'])
def user_update(account: str):
    if session.get('is_admin'):
        raise UserNotAdmin()
    user = User.query.filter_by(account=account).first()
    if not user:
        raise UserNotFound(message=f'{account}用户不存在')
    age = request.form.get('age')
    user.age = age
    user.save()
    return user.serialize()


# build_in converter [string, int, float, path, uuid] default string
@api.route('/user/<string:account>', methods=['DELETE'])
def user_delete(account):
    if not session.get('is_admin'):
        raise UserNotAdmin()

    user = User.query.filter_by(account=account).first()
    if not user:
        raise UserNotFound(message=f'{account}用户未注册')
    user.delete()
    return {'status_code': 40000, 'message': f'{account}删除成功'}


def make_cache_key_by_request():
    return str(request.values.to_dict())


@api.route('/user/login', methods=['POST'])
@cache.cached(timeout=1, make_cache_key=make_cache_key_by_request)
@limit.limit("1/second", override_defaults=False)
def user_login():
    account = request.form.get('account')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')
    user = User.query.filter_by(account=account).first()
    if not user:
        raise UserNotFound()
    if user.check_password(password):
        user.login_time = get_now()
        user.save()
        session['user_id'] = user.user_id
        session['is_admin'] = user.administrator
        if remember_me:
            session.permanent = True
    else:
        raise UserBadAuthorized()
    return user.serialize()


@api.route('/user/logout', methods=['POST'])
def user_logout():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    user.logout_time = get_now()
    user.save()
    session.clear()

    return {'status_code': 40000, 'message': f'{user.account}退出成功'}


@api.errorhandler(UserBaseException)
def error_handle(e):
    return e.serialize()
