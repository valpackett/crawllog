#!/usr/bin/env python
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from conf import *
from app import *

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def upsert_content():
    from models import setup_db
    setup_db()

if __name__ == "__main__":
    manager.run()
