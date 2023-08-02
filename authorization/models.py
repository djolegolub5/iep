from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


database = SQLAlchemy()
migrate=Migrate()


class User(database.Model):

    __tablename__="users"

    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)
    role = database.Column(database.String(256), nullable=False)


