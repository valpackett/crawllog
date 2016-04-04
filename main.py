#!/usr/bin/env python
import os
from flask.ext.script import Manager
from flask_migrate import Migrate, MigrateCommand
from conf import *
from app import *

if 'CRAWLLOG_PROD' in os.environ:
    app.debug = False
else:
    app.debug = True
    app.secret_key = 'TESTTESTKEY'

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def upsert_content():
    from models import setup_db
    setup_db()

@manager.command
def serve():
    from threading import Thread
    from following import follow_logs
    from aiohttp_wsgi import serve
    Thread(target=follow_logs).start()
    if 'CRAWLLOG_PROD' in os.environ:
        serve(app, unix_socket=os.environ['CRAWLLOG_SOCKET'], unix_socket_perms=0o660)
    else:
        print('Serving: dev')
        serve(app, port=8080)

if __name__ == "__main__":
    manager.run()
