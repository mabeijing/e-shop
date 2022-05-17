from wtforms import StringField, IntegerField, PasswordField, BooleanField
from wtforms.validators import Length, NumberRange, Email, InputRequired, DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize

from .base_validate import BaseFlaskForm, SensitiveFilter, GenderValidate


class UserFormValidate(BaseFlaskForm):
    username = StringField(label='username', validators=[
        InputRequired(message='该字段必填字段'),
        Length(min=6, max=20, message='字符串长度再6-20之间'),
        SensitiveFilter(message='输入包含敏感词汇')])

    password = PasswordField(label='password', validators=[
        InputRequired(message='该字段必填字段'),
        Length(min=6, max=20, message='密码长度再6-20之间')])

    email = StringField(label='email', validators=[
        InputRequired(message='该字段必填字段'),
        Email(message='不满足email格式')])

    nick_name = StringField(label='nick_name', validators=[
        Length(min=1, max=20, message='昵称长度再1-20之间')])

    age = IntegerField(label='age', validators=[
        NumberRange(min=0, max=100, message='年纪范围0-100之间')])

    gender = StringField(label='gender', validators=[
        InputRequired(message='该字段必填字段'), GenderValidate(message='性别只能选择男或者女')])

    role_id = IntegerField(label='role_id', validators=[
        InputRequired(message='该字段必填字段'),
        NumberRange(min=0, message='取值范围必须大于等于0')])


class UserAvatarValidate(BaseFlaskForm):
    avatar = FileField(label='avatar', validators=[
        FileRequired(message='文件不能为空'),
        FileAllowed(['jpg', 'png', 'jpeg', 'csv'], message='只支持[jpg,png,jpeg,csv]格式的文件上传'),
        FileSize(max_size=100 * 1024, message='最大支持100K')])


class UserLoginValidate(BaseFlaskForm):
    username = StringField(label='username', validators=[
        DataRequired(message='用户名必填'),
        Length(min=6, max=20, message='用户名长度6-20之间')
    ])
    password = PasswordField(label='password', validators=[
        InputRequired(message='密码不能为空'),
        Length(min=6, max=20, message='密码长度再6-20之间')
    ])
    remember_me = BooleanField(label='remember_me', validators=[

    ])
