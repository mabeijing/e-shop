from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Length
from .base_validate import BaseFlaskForm


class RoleParameterValidate(BaseFlaskForm):
    role_id = IntegerField(label='role_id', validators=[
        DataRequired(message='必填字段')
    ])
    role_name = StringField(label='role_name', validators=[
        DataRequired(message='字段必填'),
        Length(min=1, max=20, message='角色名字长度1-20之间')
    ])
    role_type = IntegerField(label='role_type', validators=[
        DataRequired(message='字段必填')
    ])
    role_description = StringField(label='role_description', validators=[
        Length(max=200, message='描述最大200字符')
    ])
