from marshmallow import Schema, fields


class BaseSchema(Schema):
    """列表返回数据固定字段"""
    delete_flag = fields.Boolean()
    create_time = fields.DateTime(format=format('%Y-%m-%d %H:%M:%S'), allow_none=True)
    update_time = fields.DateTime(format=format('%Y-%m-%d %H:%M:%S'), allow_none=True)
