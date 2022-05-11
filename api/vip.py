from flask import session, request
from . import api
from models import *
from exceptions import *


@api.route('/vip/register', methods=['POST'])
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


@api.errorhandler(VipBaseException)
def error_handle(e):
    return e.serialize()
