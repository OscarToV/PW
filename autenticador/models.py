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
    activo = db.Column(db.Integer)
    URol = db.relationship('UserRol')


    def __init__(self, username,first_name, last_name, email, password,activo):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = self.__create_password(password)
        self.activo = activo


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

class UserService(db.Model):
    __tablename__ = 'userservice'
    id = db.Column(db.Integer(),primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(66))
    hint = db.Column(db.String(20))

    def __init__(self, user_id, service_id, username, password, hint):
        self.user_id = user_id
        self.service_id = service_id
        self.username = username
        self.password = self.__create_password(password)
        self.hint = hint

    def __create_password(self,password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

class Session(db.Model):
    __tablename__='sessions'
    id = db.Column(db.Integer(), primary_key=True)
    sid = db.Column(db.String(36), unique=True)
    email = db.Column(db.String(40))
    rol = db.Column(db.String(60))
    created_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    duration = db.Column(db.Integer)

    def __init__(self,sid,email,rol,created_at,closed_at):
        self.sid = sid
        self.email = email
        self.rol = rol
        self.created_at = created_at
        self.closed_at = closed_at
        self.duration = self.__calcula_duracion(created_at, closed_at)

    def __calcula_duracion(self, ti, tf):
        t1 = ti.time()
        t2 = tf.time()

        h1 = t1.hour
        m1 = t1.minute

        h2 = t2.hour
        m2 = t2.minute

        return (h2*60+m2)-(h1*60 + m1)

class Query(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.Text())
    sql = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)

    def __init__(self, name, description, sql):
        self.name = name
        self.description = description
        self.sql = sql
