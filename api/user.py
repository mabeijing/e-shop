from flask import request, session
from exceptions import *
from . import api
from models import *
from utils import get_now


@api.route('/register', methods=['POST'])
def register():
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

    return 'pass'


@api.route('/login', methods=['POST'])
def login():
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
        if remember_me:
            session.permanent = True
    else:
        raise UserBadAuthorized()
    return user.serialize()


# string 不含/的任何字符
@api.route('/detail/<string:account>', methods=['POST'])
def detail(account):
    user = User.query.filter_by(account=account).first()
    if not user:
        raise UserNotFound(message=f'{account}用户不存在')
    else:
        if session.get('user_id') != user.user_id:
            raise UserAccessNotAuthorized()
    print(user.vip)
    return user.serialize()


@api.route('/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    user.logout_time = get_now()
    user.save()
    session.clear()

    return {'status_code': 40000, 'message': f'{user.account}退出成功'}


# build_in converter [string, int, float, path, uuid] default string
@api.route('/delete/<string:account>', methods=['POST'])
def delete_account(account):
    user = User.query.filter_by(account=account).first()
    user_id = session.get('user_id')
    admin = User.query.filter_by(id=user_id).first()
    if not admin.administrator:
        raise UserNotAdmin()
    if not user:
        raise UserNotFound(message=f'{account}用户未注册')
    user.delete()
    return {'status_code': 40000, 'message': f'{account}删除成功'}
