import os
class Config(object):
    SECRET_KEY = 'my_secret_key'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MYSQL_DATABASE_USER ='root'
    MYSQL_DATABASE_PASSWORD = ''
    MYSQL_DATABASE_DB = 'flask'
    MYSQL_DATABASE_HOST= 'localhost'
