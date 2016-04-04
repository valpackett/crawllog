import os
from flask import Flask
from flask.ext.micropub import MicropubClient
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('CRAWLLOG_DATABASE_URI', 'sqlite:////tmp/test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APPLICATION_ROOT'] = os.environ.get('CRAWLLOG_APP_ROOT', '').rstrip('/')
app.secret_key = os.environ.get('CRAWLLOG_SECRET_KEY')
db = SQLAlchemy(app)
micropub = MicropubClient(app, client_id=os.environ.get('CRAWLLOG_CLIENT_ID', 'http://localhost'))


class PrefixMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.app.config['APPLICATION_ROOT'] + environ['SCRIPT_NAME']
        return app(environ, start_response)
