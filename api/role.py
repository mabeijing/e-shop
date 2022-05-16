from api import api
from flask import session, request, jsonify
from models import *
from serialize.role import RoleQuerySchema


@api.route('/role')
def role_list():
    roles = Role.query.all()
    if not roles:
        raise

    return jsonify([role.serialize() for role in roles])
