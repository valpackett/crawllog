from flask import Flask
from flask.ext.micropub import MicropubClient
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'TESTTESTKEY'
db = SQLAlchemy(app)
micropub = MicropubClient(app, client_id='https://dc53dc54.ngrok.io')
