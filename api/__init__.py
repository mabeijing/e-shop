from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api', static_folder='/static')

from .task import *
from .goods import *
from .user import *
from .address import *
from .good_type import *
from .vip import *
from .role import *
