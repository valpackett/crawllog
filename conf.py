import os
from flask import Flask
from flask.ext.micropub import MicropubClient
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('CRAWLLOG_DATABASE_URI', 'sqlite:////tmp/test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APPLICATION_ROOT'] = os.environ.get('CRAWLLOG_APP_ROOT')
app.secret_key = os.environ.get('CRAWLLOG_SECRET_KEY')
db = SQLAlchemy(app)
micropub = MicropubClient(app, client_id=os.environ.get('CRAWLLOG_CLIENT_ID', 'http://localhost'))
