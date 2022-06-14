from flask import Blueprint, render_template, send_file
from httprunner import __version__
from httprunner.cli import run

api_runner = Blueprint('api_runner', __name__, url_prefix='/api_run')


# projectMeta 主要负责，

@api_runner.route('/version')
def version():
    return {'version': __version__}


@api_runner.route('/run')
def api_run():
    run(['-v', 'testcase/userlogin.yml', '--html=templates/report.html'])
    return render_template('report.html')


@api_runner.route('/assets/style.css')
def style_css():
    return send_file('./static/assets/style.css', mimetype='text/css')
