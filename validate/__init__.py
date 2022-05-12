from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize
from werkzeug.datastructures import ImmutableMultiDict
from wtforms import StringField, IntegerField, BooleanField, DateTimeField, FloatField
from wtforms.validators import DataRequired, EqualTo, Regexp, Length, NumberRange, Email


class BaseFlaskForm(FlaskForm):
    def __init__(self, formdata, **kwargs):
        if isinstance(formdata, dict):
            new_data = ImmutableMultiDict(formdata)
        else:
            new_data = formdata
        super().__init__(formdata=new_data, **kwargs)


class FormatJsonValidate(BaseFlaskForm):
    name = StringField(label='用户名', validators=[DataRequired(message='该字段为必填参数'),
                                                Length(min=1, max=10, message='字符串长度在1-10位数')])
    age = IntegerField(label='年纪', validators=[NumberRange(min=0, max=100, message='必须是0-100的整数'),
                                               DataRequired(message='该字段为必填参数')])


class UploadImageValidate(BaseFlaskForm):
    file = FileField('image', validators=[FileRequired(),
                                          FileAllowed(['jpg', 'png', 'jpeg', 'csv'],
                                                      message='只支持[jpg,png,jpeg,csv]格式的文件上传'),
                                          FileSize(max_size=100 * 1024, message='最大支持100K')])
