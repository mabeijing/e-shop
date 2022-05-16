from flask_wtf import FlaskForm
from werkzeug.datastructures import ImmutableMultiDict
from wtforms.validators import ValidationError

build_in_sensitive_text = ['fuck']


class GenderValidate:
    def __init__(self, message=None):
        if not message:
            message = '取值不在Enum允许范围'
        self.message = message

    def __call__(self, form, field):
        if field.data not in ['男', '女']:
            raise ValidationError(self.message)


class SensitiveFilter:

    def __init__(self, text=None, message=None):
        self.sensitive = build_in_sensitive_text
        if isinstance(text, str):
            self.sensitive.append(text)
        elif isinstance(text, (list, tuple)):
            self.sensitive.extend(text)
        if not message:
            message = '字段包含敏感词汇'
        self.message = message

    def __call__(self, form, field):
        for item in self.sensitive:
            if item in field.data:
                raise ValidationError(self.message)


class BaseFlaskForm(FlaskForm):
    """
    开启内置类型验证错误message国际化。仅支持内置类型，比如IntegerField校验非int类型报错提示
    还需要关闭 WTF_I18N_ENABLED = False
    """

    class Meta:
        locales = ['zh']

    def __init__(self, formdata, **kwargs):
        if isinstance(formdata, dict):
            new_data = ImmutableMultiDict(formdata)
        else:
            new_data = formdata
        super().__init__(formdata=new_data, **kwargs)
