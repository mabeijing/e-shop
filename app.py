import time

from flask import Flask, session, request, url_for, render_template, jsonify
from flask_limiter import RateLimitExceeded
from marshmallow.exceptions import MarshmallowError
from flask_session import Session
from flask_cors import CORS

from models import db
from settings import DEV
from tasks import ext
from web_service import socket_io
from api import api
from api_runner import api_runner
from exceptions import *
from utils import cache, limit, FlaskJSONEncoder

app = Flask(__name__, static_folder='static')
app.json_encoder = FlaskJSONEncoder
app.config.from_object(DEV)
CORS(app)
Session(app)
db.init_app(app)
app.register_blueprint(api)
app.register_blueprint(api_runner)
ext.init_app(app)
celery = ext.celery
socket_io.init_app(app, cors_allowed_origins='*')

cache.init_app(app)
limit.init_app(app)


# with app.app_context():
#     db.init_app(app)
#     db.create_all()

# @app.route("/task/<result_id>")
# def get_result(result_id):
#     result = ext.celery.AsyncResult(id=result_id)
#     return jsonify(result.result)

@app.route('/index')
def index():
    time.sleep(1)
    # return render_template('websocket_demo.html')
    return jsonify({'name': 'vmware'})


# @app.before_request
# def is_login():
#     session.permanent = False
#     white_list = [url_for('api.user_login'), url_for('api.user_register'), url_for('index')]
#     if request.path in white_list:
#         return
#     if not session.get('user_id'):
#         return UserNotLogin().serialize()


@app.errorhandler(RateLimitExceeded)
def error_handle(e):
    return {'status_code': 40050, 'message': e.description}


@app.errorhandler(HttpBaseException)
def error_handle(e):
    return e.serialize()


@app.errorhandler(MarshmallowError)
def error_handle(e):
    return {'status_code': 500, 'message': e.messages}


# @app.errorhandler(Exception)
# def error_handle(e: Exception):
#     print(e)
#     return {'status_code': 500, 'message': '服务器内部错误'}


if __name__ == '__main__':
    app.run()
    # socket_io.run(app)
