from flask import Flask, request, Response, render_template, redirect, jsonify, \
session, g, redirect, flash, url_for, abort, flash, Blueprint, make_response
from pim.models import Product
import os
import sys
import io
import csv
import json
from werkzeug import secure_filename
from main import celery
from tasks import *
from flask_paginate import Pagination, get_page_parameter
from werkzeug.contrib.cache import SimpleCache

# Implement simple cache to cache products, here we can also implement with redis and etc 

cache = SimpleCache()

# Register Blue print of app

pim_app = Blueprint('pim_app', __name__,
                        template_folder='templates')

# Allowed Extensions to check whether file format is csv or not 
ALLOWED_EXTENSIONS = set(['csv'])

# Product URI to get list of product using GET Method
@pim_app.route('/products',methods=["GET", "POST"])
def products():
    # Pagination start 
    search = False
    q = request.args.get('q')
    if q:
        search = True
    # get page params
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # search by title
    if 'search_title' in request.args:
        search_title = request.args['search_title']
        product = Product.query.filter(Product.name.contains(search_title)).all()
        print "---title"
    # search by sku
    if 'search_sku' in request.args:
        search_sku = request.args['search_sku']
        product = Product.query.filter(Product.sku.contains(search_sku)).all()
        print "---sku"
    else:
        # If there is no search keyword get all product from db 
        # Check if product is cached or not
        product = cache.get('product')
        if product is None:
            product = Product.query.all()
            # cache all products using simple cache
            cache.set('product', product, timeout=5 * 60)
        print "---all"
    # create pagination object and render to html page
    pagination = Pagination(page=page, total=len(product), search=search, record_name='product')
    return render_template('products.html' ,products=product, pagination=pagination)

# Product import URI to post product from csv file to db
@pim_app.route('/products/import', methods=['GET', 'POST'])
def product_upload():
    if request.method == 'POST':
        # check if file is in request.files or not
        if 'file' not in request.files:
            return json.dumps({'success':True, 'message':'No file part'}), 200, {'ContentType':'application/json'}
        file = request.files['file']
        # if file name is none
        if file.filename == '':
            return json.dumps({'success':True, 'message':'No compatible file'}), 200, {'ContentType':'application/json'}
        #  if file extension is csv or not
        if file and allowed_file(file.filename):
            file_name = secure_filename(file.filename)
            #  temporary saving file to access through background task
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            # get information of file
            fileinfo = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            # check if file size is less than 100MB and Greater than 1KB
            if fileinfo.st_size >= 1000 and fileinfo.st_size <=100000000:
                # if file size is correct than schedule a background task to acess files and put data into database
                schedule_csv_upload = read_csv_file.apply_async(args=[os.path.join(app.config['UPLOAD_FOLDER'], file_name)], countdown=60)
                return jsonify({}), 202, {'Location': url_for('pim_app.taskstatus',
                                                  task_id=schedule_csv_upload.id), "Message":"Background Job created to upload product in database"}
            else:
                
                return jsonify({}), 202, {"Message":"file size is not compatible"} 
                # json.dumps({'success':True, 'message':'file size is not compatible'}), 200, {'ContentType':'application/json'}
        else:
            return jsonify({}), 202, {"Message":"file extension is not compatible"} 
            # json.dumps({'success':True, 'message':'file extension is not compatible'}), 200, {'ContentType':'application/json'}
            # return redirect('/products')
    return redirect('/products')
    # render_template('upload.html')

# check is file extension is valid or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# get status of schedule background task
@pim_app.route('/status/<task_id>')
def taskstatus(task_id):
    task = read_csv_file.AsyncResult(task_id)
    if task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': task.state
        }
    else:
        response = {
                'state': "Failed",
                'current': 1,
                'total': 1,
                'status': task.info
        }
    return jsonify(response)


