class BasicException(Exception):
    status_code = 200
    message = '操作成功'

    def __init__(self, status_code: int = None, message: str = None):
        super().__init__()
        if status_code:
            self.status_code = status_code
        if message:
            self.message = message

    def __str__(self):
        return str(self.serialize())

    def serialize(self) -> dict:
        return {'status_code': self.status_code, 'message': self.message}


class HttpBaseException(BasicException):
    pass


class RoleBaseException(BasicException):
    pass


class UserBaseException(BasicException):
    pass


class GoodBaseException(BasicException):
    pass


class GoodTypeBaseException(BasicException):
    pass


class VipBaseException(BasicException):
    pass


class AddressBaseException(BasicException):
    pass


class UserNotFound(UserBaseException):
    status_code = 40010
    message = '用户未注册'


class UserAlreadyExists(UserBaseException):
    status_code = 40011
    message = '用户已注册'


class UserAccessNotAuthorized(UserBaseException):
    status_code = 40012
    message = '用户操作未授权'


class UserNotLogin(UserBaseException):
    status_code = 40013
    message = '用户未登录'


class UserBadAuthorized(UserBaseException):
    status_code = 40014
    message = '用户名或密码错误'


class UserNotAdmin(UserBaseException):
    status_code = 40015
    message = '非管理员无法操作'


class FileNotFound(UserBaseException):
    status_code = 40016
    message = '上传的文件不存在'


class AddressNotFound(AddressBaseException):
    status_code = 40020
    message = '地址不存在'


class UserParameterError(UserBaseException):
    status_code = 40021
    message = '参数错误'


class GoodTypeNotFound(GoodTypeBaseException):
    status_code = 40030
    message = '货物分类不存在'


class ContentTypeError(HttpBaseException):
    status_code = 40040
    message = 'Content-Type类型错误'


class RoleParameterError(RoleBaseException):
    status_code = 40050
    message = '参数错误'


class RoleNotFound(RoleBaseException):
    status_code = 40051
    message = 'role不存在'
