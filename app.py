from flask_cors import CORS
from flask import Flask, session, request, url_for, render_template
from models import db
from settings import DEV
from utils import ext
from web_service import socket_io
from api import api
from exceptions import UserNotLogin

app = Flask(__name__, static_folder='static')
app.config.from_object(DEV)
CORS(app)
db.init_app(app)
app.register_blueprint(api)
ext.init_app(app)
socket_io.init_app(app, cors_allowed_origins='*')


# with app.app_context():
#     db.init_app(app)
#     db.create_all()

# @app.route("/task/<result_id>")
# def get_result(result_id):
#     result = ext.celery.AsyncResult(id=result_id)
#     return jsonify(result.result)

@app.route('/index')
def index():
    return render_template('websocket_demo.html')


@app.before_request
def is_login():
    white_list = [url_for('api.user_login'), url_for('api.user_register'), url_for('index')]
    if request.path in white_list:
        return
    if not session.get('user_id'):
        raise UserNotLogin()


@app.errorhandler(Exception)
def error_handle(e: Exception):
    print(e)
    return {'status_code': 500, 'message': '服务器内部错误'}


if __name__ == '__main__':
    # app.run()
    socket_io.run(app)
