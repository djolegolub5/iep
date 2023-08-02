from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from configuration import Configuration
from models import database
from sqlalchemy_utils import database_exists, create_database

app=Flask(__name__)
app.config.from_object(Configuration)

database.init_app(app)

migrate=Migrate(app,database)

manager=Manager(app)
manager.add_command("db",MigrateCommand)

if (__name__=='__main__'):
    if (not database_exists(Configuration.SQLALCHEMY_DATABASE_URI)):
        create_database(Configuration.SQLALCHEMY_DATABASE_URI)
    manager.run()