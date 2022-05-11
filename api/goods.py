import os
from flask import request, jsonify
from werkzeug.utils import secure_filename

from . import api
from models import *
from utils import image_md5


@api.route('/goods/add', methods=['POST'])
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


@api.route('/api/goods', methods=['POST', 'GET'])
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


@api.route('/goods/<int:good_id>', methods=['POST'])
def good_detail(good_id: int):
    good = Goods.query.filter_by(id=good_id).first()
    if not good:
        return {'code': 40404, 'msg': '未找到该货物'}
    return good.serialize()


@api.route('/goods/delete', methods=['DELETE'])
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
