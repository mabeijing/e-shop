from flask import session, jsonify, request

from . import api
from models import *
from exceptions import *


@api.route('/address/list')
def get_address():
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    address_list = user.address.filter_by(user_id=user_id).all()
    return jsonify([address.serialize() for address in address_list])


@api.route('/address/add', methods=['POST'])
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


@api.route('/address/<int:address_id>', methods=['PUT'])
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
        print(e)
        raise e
    address = user.address.filter_by(id=address_id).first()
    return address.serialize()


@api.route('/address/<int:address_id>', methods=['DELETE'])
def delete_address(address_id: int):
    address = Address.query.filter_by(id=address_id).first()
    if not address:
        raise AddressNotFound()
    address.delete()
    return {'status': 40000, 'message': '删除成功'}


@api.errorhandler(AddressBaseException)
def error_handle(e):
    return e.serialize()
