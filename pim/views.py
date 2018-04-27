from flask import request, render_template, redirect, jsonify, url_for, Blueprint
from pim.models import Product
import json
from werkzeug import secure_filename
from tasks import read_csv_file
from main import app
import os
from flask_paginate import Pagination, get_page_parameter
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()

pim_app = Blueprint('pim_app', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = set(['csv'])


# Product URI to get list of product using GET Method
@pim_app.route('/products', methods=["GET", "POST"])
def products():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    if 'search_title' in request.args and len(request.args['search_title']) != 0:
        search_title = request.args['search_title']
        product = Product.query.filter(Product.name.contains(search_title)).all()
    elif 'search_sku' in request.args and len(request.args['search_sku']) != 0:
        search_sku = request.args['search_sku']
        product = Product.query.filter(Product.sku.contains(search_sku)).all()
    else:
        product = cache.get('product')
        if product is None:
            product = Product.query.all()
            cache.set('product', product, timeout=5 * 60)
    pagination = Pagination(page=page, total=len(product), search=search, record_name='product')
    return render_template('products.html', products=product, pagination=pagination)


# Product import URI to post product from csv file to db
@pim_app.route('/products/import', methods=['GET', 'POST'])
def product_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return json.dumps({'success': True, 'message': 'No file part'}), 200, {'ContentType': 'application/json'}
        file = request.files['file']
        if file.filename == '':
            return json.dumps({'success': True, 'message': 'No compatible file'}), 200, {'ContentType': 'application/json'}
        if file and allowed_file(file.filename):
            file_name = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            fileinfo = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            if fileinfo.st_size >= 1000 and fileinfo.st_size <= 100000000:
                schedule_csv_upload = read_csv_file.apply_async(args=[os.path.join(app.config['UPLOAD_FOLDER'], file_name)], countdown=60)
                return jsonify({}), 202, {'Location': url_for('pim_app.taskstatus', task_id=schedule_csv_upload.id), "Message": "Background Job created to upload product in database"}
            else:
                return jsonify({}), 202, {"Message": "file size is not compatible"}
        else:
            return jsonify({}), 202, {"Message": "file extension is not compatible"}
    return redirect('/products')


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
