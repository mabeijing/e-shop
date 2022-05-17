from api import api
from flask import request, jsonify
from models import *
from utils import is_administrator
from validate import *
from exceptions import *


@api.route('/role')
@is_administrator
def role_list():
    roles = Role.query.all()
    return jsonify([role.serialize() for role in roles])


@api.route('/role', methods=['POST'])
@is_administrator
def add_role():
    role_form = RoleParameterValidate(request.form)
    if not role_form.validate():
        raise RoleParameterError(message=role_form.errors)
    role = Role(**role_form.data)
    role.save()
    return jsonify(role.serialize())


@api.route('/role/<int:role_id>', methods=['PUT'])
@is_administrator
def role_edit(role_id):
    role_form = RoleParameterValidate(request.json)
    if not role_form.validate():
        raise RoleParameterError(message=role_form.errors)
    role_query = Role.query.filter_by(role_id=role_id)
    try:
        role_query.update(role_form.data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e from Exception
    role = role_query.first()
    return role.serialize()


@api.route('/role/<int:role_id>', methods=['DELETE'])
@is_administrator
def role_delete(role_id):
    role = Role.query.filter_by(role_id=role_id).first()
    if not role:
        raise RoleNotFound(message=f'{role_id}不存在')
    role.delete()
    return {'status_code': 40000, 'message': '删除成功'}


@api.errorhandler(RoleBaseException)
def error_handle(e):
    return e.serialize()
