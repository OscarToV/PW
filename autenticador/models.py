from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(40))
    password = db.Column(db.String(66))
    created_date = db.Column(db.DateTime, default = datetime.datetime.now)
    URol = db.relationship('UserRol')


    def __init__(self, username,first_name, last_name, email, password):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = self.__create_password(password)


    def __create_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password,password)

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    code = db.Column(db.String(60))
    URol = db.relationship('UserRol')

    def __init__(self, name, code):
        self.name = name
        self.code = code


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))

    def __init__(self, name):
        self.name = name

class UserRol(db.Model):
    __tablename__ = 'userrol'
    id = db.Column(db.Integer(), primary_key=True)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    started_by = db.Column(db.String(40))
    finished_by = db.Column(db.String(40))
    started_at =  db.Column(db.DateTime, default = datetime.datetime.now)
    finished_at = db.Column(db.DateTime, default=None)
    finished_reason = db.Column(db.Text())
    comment = db.Column(db.Text())

    def __init__(self, rol_id, user_id, started_by):
        self.rol_id = rol_id
        self.user_id = user_id
        self.started_by = started_by
