from flask import request, jsonify
from . import api
from models import *
from exceptions import *


@api.route('/goods_type/list')
def good_type_list():
    good_list = GoodType.query.all()
    goods_li = [good.serialize() for good in good_list] if good_list else []
    return jsonify(goods_li)


@api.route('/goods_type/add', methods=['POST'])
def add_good_type():
    name = request.form.get('name')
    good = GoodType(name=name)
    good.save()
    return good.serialize()


@api.route('/goods_type/<int:good_id>', methods=['PUT'])
def edit_good_type(good_id: int):
    good = GoodType.query.filter_by(id=good_id).first()
    if not good:
        raise GoodTypeNotFound()
    form = request.form.to_dict()
    try:
        GoodType.query.filter_by(id=good_id).update(form)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return good.serialize()


@api.route('/goods_type/<int:good_id>', methods=['DELETE'])
def delete_good_type(good_id: int):
    good = GoodType.query.filter_by(id=good_id).first()
    if not good:
        raise GoodTypeNotFound()
    good.delete()
    return {'status': 40000, 'message': '删除成功'}


@api.errorhandler(GoodTypeBaseException)
def error_handle(e):
    return e.serialize()
