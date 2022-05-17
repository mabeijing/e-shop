import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from serialize.role import RoleQuerySchema, UserQuerySchema

from utils import generate_uid

"""
默认外键，主键数据删除，外键更新null
    parent_id = Column(Integer, ForeignKey('parent.id'))
    parent = relationship("Parent", backref=backref("child"))
 
    ###  只删除父级，子不影响
    # 1. parent_id = Column(Integer, ForeignKey('parent.id', ondelete="CASCADE"))
    #    parent = relationship("Parent", backref=backref("child", passive_deletes=True))
 
    ###  子级跟随删除
    # 2. parent = relationship("Parent", backref = backref("child", cascade="all, delete-orphan"))
    # 3. parent = relationship("Parent", backref = backref("child", cascade="all,delete"))
 
    ##  父级删除，子级不删除，外键更新为 null
一对多配置
    parent_id = Column(Integer, ForeignKey('parent.id'), unique=True)  
    ### 这个就表示N对一。如果指定了唯一约束，表示每个child的parent都是唯一的，
    parent = relationship("Parent", backref=backref("child"), uselist=False)   
    ### 这个配置，可以通过child查询到对应id的parent
    ### 个人觉得，只有ChildModel加上 唯一约束和反向查询单一查询，才是一对一
    ### 如果不配置唯一约束，取消反向单一查询，可以不同的child有相同的parent，就是一对多
    
组合用法useless=True, lazy='dynamic' 这个表示延迟加载，
print(user.vip.all()) 必须使用all()才会执行擦汗寻。vip返回AppenderBaseQuery对象
如果usrlist=False，不可以配置lazy属性，表示直接在家，user.vip就可以拿到结果。

"""

db = SQLAlchemy()

goodCourt = db.Table('GoodsCourt',
                     db.Column('GOOD_ID', db.Integer, db.ForeignKey('tb_goods.ID')),
                     db.Column('COURT_ID', db.Integer, db.ForeignKey('tb_court.ID')))


class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, name='ID')
    delete_flag = db.Column(db.Boolean, default=False, name='DELETE_FLAG')
    create_time = db.Column(db.DateTime, default=datetime.now, name='CREATE_TIME')
    update_time = db.Column(db.DateTime, onupdate=datetime.now, name='UPDATE_TIME')

    def save(self) -> bool:
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        else:
            return True

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def serialize(self):
        serialize = self.__serialize__()
        value = serialize.dumps(self, ensure_ascii=False)
        return serialize.loads(value)


# class OperationRecord(BaseModel):
#     """
#     操作记录表
#
#     """
#     __tablename__ = 'tb_operation_record'


class Role(BaseModel):
    """
    角色和用户，一对多
    """
    __tablename__ = 'tb_role'
    __serialize__ = RoleQuerySchema
    role_id = db.Column(db.Integer, nullable=False, index=True, unique=True, name='ROLE_ID', comment='角色ID')
    role_name = db.Column(db.String(32), nullable=False, unique=True, name='ROLE_NAME', comment='角色名字')
    role_type = db.Column(db.Integer, nullable=False, unique=True, name='ROLE_TYPE', comment='角色类型')
    role_description = db.Column(db.TEXT, default='', name='ROLE_DESCRIPTION', comment='角色描述')

    users = db.relationship("User", backref='role')

    def __repr__(self):
        return f'{self.__class__.__name__}(role_name={self.role_name})'


class User(BaseModel):
    __tablename__ = 'tb_user'
    __serialize__ = UserQuerySchema
    # __table_args__ = (
    #     db.UniqueConstraint('user_id', 'post_id', name='uix_user_post_user_id_post_id'),
    #     db.Index('ix_user_post_user_id_insert_time', 'user_id', 'insert_time')
    # )
    user_id = db.Column(db.String(64), default=generate_uid, index=True, unique=True, name='USER_ID', comment='用户ID')
    nick_name = db.Column(db.String(32), name='NICK_NAME', comment='昵称')
    email = db.Column(db.String(64), unique=True, nullable=False, name='EMAIL', comment='邮件')
    username = db.Column(db.String(32), unique=True, nullable=False, name='USERNAME', comment='用户名')
    _password = db.Column(db.String(256), nullable=False, name='PASSWORD', comment='密码')
    avatar = db.Column(db.String(256), name='AVATAR', comment='头像缩略图')
    age = db.Column(db.Integer, name='AGE', comment='年龄')
    gender = db.Column(db.Enum('男', '女'), server_default='男', nullable=False, name='GENDER', comment='性别')
    login_time = db.Column(db.DateTime, name='LOGIN_TIME', comment='最近一次登录时间')

    address = db.relationship('Address', backref="user", lazy="dynamic")
    role_id = db.Column(db.Integer, db.ForeignKey('tb_role.ROLE_ID'), nullable=False, name='ROLE_ID',
                        comment='外键ROLE_ID')

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, pwd) -> bool:
        return check_password_hash(self._password, pwd)

    def __repr__(self):
        return f'{self.__class__.__name__}(username={self.username})'


class Vip(BaseModel):
    __tablename__ = 'tb_vip'
    name = db.Column(db.String(50), name='NAME')
    level = db.Column(db.Integer, default=0, name='LEVEL')
    user_id = db.Column(db.String(64), db.ForeignKey('tb_user.USER_ID'), unique=True, name='USER_ID')  # 每个user可能有多个vip。

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name})'


class Court(BaseModel):
    __tablename__ = 'tb_court'
    user_id = db.Column(db.String(64), db.ForeignKey('tb_user.USER_ID'), name='USER_ID')
    NUMBER = db.Column(db.Integer, default=0)
    GOODS = db.relationship('Goods', secondary=goodCourt, backref=db.backref("tb_court", lazy="dynamic"),
                            lazy="dynamic")

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class Address(BaseModel):
    __tablename__ = 'tb_address'
    province = db.Column(db.String(28), name='PROVINCE')
    city = db.Column(db.String(28), name='CITY')
    county = db.Column(db.String(28), name='COUNTY')
    detail = db.Column(db.String(256), default=province + city + county, name='DETAIL')
    user_id = db.Column(db.String(64), db.ForeignKey('tb_user.USER_ID'), name='USER_ID')

    # good = db.relationship('Goods', backref='address', uselist=True)  # 一个地址可以查询出一个货物列表，如果货物配置了地址外键，就是一对多

    def __repr__(self):
        return f'{self.__class__.__name__}(detail={self.detail})'


class AD(BaseModel):
    __tablename__ = 'tb_ad'
    CONTENT = db.Column(db.String(50))
    DISPLAY_TIME = db.Column(db.DateTime)
    END_TIME = db.Column(db.DateTime)
    IMAGE = db.Column(db.String(256))
    VIDEO = db.Column(db.String(256))
    TITLE = db.Column(db.String(128))
    INTRO = db.Column(db.String(512))

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.ID})'


class Admin(BaseModel):
    __tablename__ = 'tb_admin'
    NAME = db.Column(db.String(32))
    ACCOUNT = db.Column(db.String(16))
    PASSWORD = db.Column(db.String(128))
    LEVEL = db.Column(db.Integer, default=0)
    LOGIN_TIME = db.Column(db.DateTime)
    LOGOUT_TIME = db.Column(db.DateTime)

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.ID})'


class Goods(BaseModel):
    __tablename__ = 'tb_goods'
    good_name = db.Column(db.String(128), name='GOOD_NAME')
    good_type_id = db.Column(db.Integer, db.ForeignKey('tb_good_type.ID'), name='GOOD_TYPE_ID')
    origin_price = db.Column(db.Float(10), name='ORIGIN_PRICE')
    sell_price = db.Column(db.Float(10), name='SELL_PRICE')
    contains = db.Column(db.Integer, default=0, name='CONTAINS')
    produce_time = db.Column(db.DateTime, name='PRODUCE_TIME')
    expire_time = db.Column(db.DateTime, name='EXPIRE_TIME')
    image = db.Column(db.String(256), name='IMAGE')
    location = db.Column(db.Integer, db.ForeignKey('tb_address.ID'))  # 查询关联货物的地址
    send_address = db.Column(db.Integer, db.ForeignKey('tb_address.ID'))
    intro = db.Column(db.String(512), name='INTRO')
    look_times = db.Column(db.Integer, default=0, name='LOOK_TIMES')
    buy_times = db.Column(db.Integer, default=0, name='BUY_TIMES')
    like_times = db.Column(db.Integer, default=0, name='LIKE_TIMES')

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class GoodType(BaseModel):
    __tablename__ = 'tb_good_type'
    name = db.Column(db.String(64), name='NAME')
    number = db.Column(db.Integer, default=0, name='NUMBER')

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class VipReceipt(BaseModel):
    __tablename__ = 'tb_vip_receipt'
    order_no = db.Column(db.String(50), name='ORDER_NO')
    pay_value = db.Column(db.Float(10), name='PAY_VALUE')
    cur_of_value = db.Column(db.Float(10), name='CUT_OF_VALUE')
    vip_id = db.Column(db.Integer, db.ForeignKey('tb_vip.ID'), name='VIP_ID')

    user_id = db.Column(db.String(64), db.ForeignKey('tb_user.USER_ID'), name='USER_ID')

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class Receipt(BaseModel):
    __tablename__ = 'tb_receipt'
    order_no = db.Column(db.String(50), name='ORDER_NO')
    pay_value = db.Column(db.Float(10), name='PAY_VALUE')
    cur_of_value = db.Column(db.Float(10), name='CUT_OF_VALUE')
    item_id = db.Column(db.JSON, default=[], name='ITEM_ID')

    user_id = db.Column(db.String(64), db.ForeignKey('tb_user.USER_ID'), name='USER_ID')

    def get_goods_id_list(self):
        str_list = json.loads(self.item_id)
        id_list = []
        for item in str_list:
            id_list.append(int(item))
        return id_list

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class ReceiptItem(BaseModel):
    __tablename__ = 'tb_receipt_item'
    good_id = db.Column(db.Integer, name='GOOD_ID')
    number = db.Column(db.Integer, default=0, name='NUMBER')

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class Comment(BaseModel):
    __tablename__ = 'tb_comment'
    content = db.Column(db.String(512), name='CONTENT')
    points = db.Column(db.Integer, default=5, name='POINTS')
    screen_cut = db.Column(db.String(256), name='SCREEN_CUT')
    user_id = db.Column(db.String(64), db.ForeignKey('tb_user.USER_ID'), name="USER_ID")
    good_id = db.Column(db.Integer, db.ForeignKey('tb_goods.ID'), name='GOOD_ID')

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'
