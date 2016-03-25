from flask.ext.script import Manager
from flask_migrate import Migrate, MigrateCommand
from conf import *

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def upsert_content():
    from db import setup_db
    setup_db()

@manager.command
def serve():
    from threading import Thread
    from following import follow_logs
    Thread(target=follow_logs).start()
    app.debug = True
    from aiohttp_wsgi import serve
    serve(app)

if __name__ == "__main__":
    manager.run()
