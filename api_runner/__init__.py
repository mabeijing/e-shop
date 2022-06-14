from flask import Blueprint
from httprunner import __version__

api_runner = Blueprint('api_runner', __name__, url_prefix='/api_run', static_folder='/static')


# projectMeta 主要负责，

@api_runner.route('/version')
def version():
    return {'version': __version__}


