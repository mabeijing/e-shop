from marshmallow import Schema, fields, EXCLUDE

from serialize.base_serialize import BaseSchema


class UserQuery(BaseSchema):
    class Meta:
        unknown = EXCLUDE

    user_id = fields.Str()
    nick_name = fields.Str()
    username = fields.Str()
    avatar = fields.Str(allow_none=True)
    age = fields.Int()
    id_card = fields.Str()
    gender = fields.Str()
    login_time = fields.DateTime(allow_none=True)
    balance = fields.Float()
    role_id = fields.Int()


class UserQuerySchema(BaseSchema):
    class Meta:
        unknown = EXCLUDE

    user_id = fields.Str()
    nick_name = fields.Str()
    username = fields.Str()
    avatar = fields.Str(allow_none=True)
    age = fields.Int()
    id_card = fields.Str()
    gender = fields.Str()
    login_time = fields.DateTime(allow_none=True)
    balance = fields.Float()
    role_id = fields.Int()
    _role = fields.Dict()


class RoleQuery(BaseSchema):
    class Meta:
        unknown = EXCLUDE

    role_id = fields.Int()
    role_name = fields.String()
    role_type = fields.String()
    role_description = fields.Str()


class RoleQuerySchema(BaseSchema):
    """查询参数序列化
    执行过程，首先会通过role_id字段拿到值，再用当前值，通过fields.Int()去序列化。
    """

    class Meta:
        unknown = EXCLUDE

    role_id = fields.Int()
    role_name = fields.String()
    role_type = fields.String()
    role_description = fields.Str()
    users_list = fields.List(fields.Dict())


class ProjectQuerySchema(Schema):
    """查询参数序列化"""

    class Meta:
        """
        RAISEValidationError （默认）：如果有任何未知字段，则引发 err
        EXCLUDE: 排除未知字段
        INCLUDE：接受并包含未知字段
        """
        unknown = EXCLUDE

    id = fields.Int()
    ids = fields.List(fields.Str() or fields.Int())
    name = fields.Str()
    order_field = fields.Str()
    sort_type = fields.Int()
    created_by_name = fields.Str()


class ProjectListSchema(BaseSchema):
    """项目序列化"""
    id = fields.Int()
    name = fields.Str()
    responsible_name = fields.Str()
    test_user = fields.Str()
    dev_user = fields.Str()
    publish_app = fields.Str()
    simple_desc = fields.Str()
    remarks = fields.Str()
    config_id = fields.Int()
    run_status = fields.Str()
    product_id = fields.Int()
