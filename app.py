from flask_cors import CORS
from flask import Flask, session, request, url_for, render_template
from validate import FormatJsonValidate, UploadImageValidate
from models import db
from settings import DEV
from tasks import ext
from web_service import socket_io
from api import api
from exceptions import *
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
app.config.from_object(DEV)
CORS(app)
db.init_app(app)
app.register_blueprint(api)
ext.init_app(app)
celery = ext.celery
socket_io.init_app(app, cors_allowed_origins='*')


@app.route('/format_json')
def format_json():
    data_form = FormatJsonValidate(request.args)
    if not data_form.validate():
        return data_form.errors
    image_form = UploadImageValidate(request.files)
    if not image_form.validate():
        return image_form.errors

    headers = request.headers
    # if headers.get('Content-Type') != 'application/json':
    #     raise ContentTypeError(message='Content-Type必须是(application/json)')

    filename = secure_filename(image_form.file.data.filename)
    image_form.file.data.save(filename)
    return data_form.data


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
        return UserNotLogin().serialize()


@app.errorhandler(HttpBaseException)
def error_handle(e):
    return e.serialize()


@app.errorhandler(Exception)
def error_handle(e: Exception):
    print(e)
    return {'status_code': 500, 'message': '服务器内部错误'}


if __name__ == '__main__':
    # app.run()
    socket_io.run(app)
