from flask import request, session, jsonify
from werkzeug.utils import secure_filename

from . import api
from models import *
from utils import get_now, cache, limit, is_administrator
from validate import *
from exceptions import *


@api.route('/user/register', methods=['POST'])
def user_register():
    user_form = UserFormValidate(request.form)
    if not user_form.validate():
        raise UserParameterError(message=user_form.errors)
    username = user_form.username.data
    if User.query.filter_by(username=username).first():
        raise UserAlreadyExists(message=f'{username}已存在。')

    email = user_form.email.data
    if User.query.filter(User.email == email).first():
        raise UserAlreadyExists(message=f'{email}已存在。')

    user = User(**user_form.data)
    user.save()
    return jsonify(user.serialize())


@api.route('/users')
def user_list():
    users = User.query.all()
    return jsonify([u.serialize() for u in users])


# string 不含/的任何字符
@api.route('/user/<string:username>', methods=['POST'])
@is_administrator
def user_detail(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        raise UserNotFound(message=f'{username}用户不存在')
    return jsonify(user.serialize())


@api.route('/user/<string:username>', methods=['PUT'])
@is_administrator
def user_edit(username: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        raise UserNotFound(message=f'{username}用户不存在')
    age = request.form.get('age')
    user.age = age
    user.save()
    return jsonify(user.serialize())


@api.route('/user/avatar', methods=['POST'])
def user_avatar():
    file_form = UserAvatarValidate(request.files)
    if not file_form.validate():
        raise FileNotFound(message=file_form.errors)
    filename = secure_filename(file_form.avatar.data.filename)
    avatar_path = '/static/uploads/' + filename
    file_form.avatar.data.save('static/uploads/'+filename)

    user_id = session.get('user_id')
    try:
        User.query.filter_by(user_id=user_id).update({'avatar': avatar_path})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e from Exception

    user = User.query.filter_by(user_id=user_id).first()
    return jsonify(user.serialize())


# build_in converter [string, int, float, path, uuid] default string
@api.route('/user/<string:username>', methods=['DELETE'])
@is_administrator
def user_delete(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        raise UserNotFound(message=f'{username}用户未注册')
    user.delete()
    return {'status_code': 40000, 'message': f'{username}删除成功'}


def _make_cache_key_by_request():
    return str(request.values.to_dict())


@api.route('/user/login', methods=['POST'])
@cache.cached(timeout=1, make_cache_key=_make_cache_key_by_request)
@limit.limit("1/second", override_defaults=False)
def user_login():
    user_form = UserLoginValidate(request.json)
    if not user_form.validate():
        raise UserParameterError(message=user_form.errors)
    user = User.query.filter_by(username=user_form.username.data).first()
    if not user:
        raise UserNotFound()
    if user.check_password(user_form.password.data):
        user.login_time = get_now()
        user.save()
        session['user_id'] = user.user_id
        session['role_id'] = user.role_id
        session['username'] = user.username
        if user_form.remember_me.data:
            session.permanent = True
        return jsonify(user.serialize())
    else:
        raise UserBadAuthorized()


@api.route('/user/logout', methods=['POST'])
def user_logout():
    username = session.get('username')
    session.clear()
    return {'status_code': 40000, 'message': f'{username}退出成功'}


@api.errorhandler(UserBaseException)
def error_handle(e):
    return e.serialize()
