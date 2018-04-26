from flask import Flask

from flask_sqlalchemy import SQLAlchemy
DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test-4.db'

# with sqlite3.connect(db_path) as db:

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
