from flask import Flask, request, Response, render_template, redirect, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import flash, url_for
import csv,io,os,sys,jinja2
from werkzeug import secure_filename
from config import Config, DevelopmentConfig
from celery import Celery

app = Flask(__name__)

app_name = 'PIM_WEB'

# Template load
template_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('./pim_web/templates'),
])


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.config['UPLOAD_FOLDER'] = os.getcwd()+'/uploads'

app.jinja_loader = template_loader

# Using celery to run background task
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
# app.config.from_object(DevelopmentConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////%s/product.db' %os.getcwd()

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)

db.init_app(app)

print db
# host = 'http://localhost:5000/'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], include=['tasks'])

celery.conf.update(app.config)

# get status of schedule background task
@app.route('/')
def root_uri_dummy():
    return "Go to the Product"

if __name__ == '__main__':
    app.secret_key = 'atulsecretkey'
    #  using gevent WSGIServer to handle request
    from gevent.wsgi import WSGIServer
    http_server = WSGIServer((), app)
    http_server.serve_forever()

