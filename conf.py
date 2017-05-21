import os
import sys
import logging
import models
from flask import Flask
from flask_micropub import MicropubClient
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('CRAWLLOG_DATABASE_URI', 'sqlite:////tmp/test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APPLICATION_ROOT'] = os.environ.get('CRAWLLOG_APP_ROOT', '').rstrip('/')
if 'CRAWLLOG_PROD' in os.environ:
    app.debug = False
    app.secret_key = os.environ.get('CRAWLLOG_SECRET_KEY')
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
else:
    app.debug = True
    app.secret_key = 'TESTTESTKEY'
db = SQLAlchemy(app)
db.register_base(models.Model)
micropub = MicropubClient(app, client_id=os.environ.get('CRAWLLOG_CLIENT_ID', 'http://localhost'))


prefixed_app = None

if app.config['APPLICATION_ROOT'] != '':
    class PrefixMiddleware(object):
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            environ['SCRIPT_NAME'] = self.app.config['APPLICATION_ROOT'] + environ['SCRIPT_NAME']
            return app(environ, start_response)

    prefixed_app = PrefixMiddleware(app)
