from flask_env import MetaFlaskEnv
import mysql.connector
from mysql.connector import pooling
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask import Flask, render_template, redirect, url_for, make_response, request, flash
import uuid
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import argon2
import json
import base64
from filedownload import FileDownload
from fileupload import FileUpload
import os
import ast

class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "adminonlineshopsecretkey"
    WTF_CSRF_SECRET_KEY = "adminonlineshopsecretkey"
    WTF_CSRF_TIME_LIMIT = 604800
    COOKIE = "ADMIN-ONLINE-SHOP-KEY"
    ADMIN_USER = "USER"
    HOST = "127.0.0.1"
    DB = "online-shop"
    USERS = "admin"
    PASSWORD = "thisisasecretkey"
    PORT = 3306
    ITEMS_TABLE = "items"
    ORDERS_TABLE = "orders"
    UPLOAD_TABLE = "upload"
    PRODUCTS_TABLE = "products"
    USERS_TABLE = "users"
    MINIO_API_URL = "34.71.225.137:9000"
    MINIO_ACCESS_KEY = "socratesaccesskey"
    MINIO_SECRET_KEY = "socratessecretkey2020"
    MINIO_SECURE = False
    MINIO_BUCKET_NAME = "testlifecycle"
    UPLOAD_PATH = '/tmp'

app = Flask(__name__)
csrf = CSRFProtect(app)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    form = LoginForm()
    return render_template('login.html', form=form, message="Session expired: {}".format(e.description))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

def from_js_to_python_deserialize(b64data):
    """
    b64 encoded byte stream -> b64 decoded byte stream -> json string -> python dictionary.
    The js side use: JSON.stringify() -> btoa()
    :param b64data: Base 64 encoded data
    :return: python dictionary
    """
    ret = {}
    try:
        ret = json.loads(base64.b64decode(b64data).decode('utf-8'))
    except:
        pass
    finally:
        return ret

def from_python_to_js_serialization(pythondict):
    """
    pythondict -> json string -> byte array -> b64 encode
    The js side use: string.replace() to remove &#39 garbage -> JSON.parse() -> atob()
    :param pythondict:
    :return:
    """
    return base64.b64encode(json.dumps(pythondict).encode('utf-8'))

def update_product(id, title, description, price, images):
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_update_query = f"update {app.config['ITEMS_TABLE']} set title=%s, description=%s, price=%s, images=%s where id=%s"
    try:
        c.execute(mysql_update_query,(title, description, price, images, id))
        conn.commit()
        ret = 'Inserted', 200
    except Exception as e:
        ret = str(e), 404
    c.close()
    conn.close()
    return ret


def add_product(title, description, price, images):
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_add_query = f"insert into {app.config['ITEMS_TABLE']} (title, description, price, images) values (%s,%s,%s,%s)"
    try:
        c.execute(mysql_add_query,(title, description, price, images))
        conn.commit()
        ret = 'Inserted', 200
    except Exception as e:
        ret = str(e), 404
    c.close()
    conn.close()
    return ret

def get_product_by_id(id):
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select * from {app.config['ITEMS_TABLE']} where id=%s"
    c.execute(mysql_select_query, (id,))
    product = c.fetchone()
    if product is not None:
        if product[4] is not None:
            images = ast.literal_eval(product[4])
            resp = {'id': product[0], 'title': product[1], 'description': product[2], 'price': product[3],
                    'images': images}
        else:
            resp = {'id': product[0], 'title': product[1], 'description': product[2], 'price': product[3]}
    else:
        resp = {}
    c.close()
    conn.close()
    return resp

def get_products():
    response = []
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select * from {app.config['ITEMS_TABLE']}"
    c.execute(mysql_select_query)
    products = c.fetchall()
    if len(products) != 0:
        for product in products:
            if product[4] is not None:
                images = ast.literal_eval(product[4])
                resp = {'id':product[0], 'title': product[1], 'description': product[2], 'price': product[3], 'images': images}
            else:
                resp = {'id': product[0], 'title': product[1], 'description': product[2], 'price': product[3]}
            response.append(resp)
    c.close()
    conn.close()
    return response


def get_name_item(itemid):
    conn = cnxpool.get_connection()
    c = conn.cursor(buffered=True)
    mysql_select_query = f"select i.title, p.quantity from {app.config['ITEMS_TABLE']} i join {app.config['PRODUCTS_TABLE']} p on " \
                         f"i.id = p.itemid where p.itemid = %s"
    c.execute(mysql_select_query, (itemid,))
    item = c.fetchone()
    if item is not None:
        ret = {'item': item[0], 'quantity': item[1]}
    else:
        ret = {}
    c.close()
    conn.close()
    return ret

def get_order_itemid(identified):
    ids = []
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select itemid from {app.config['PRODUCTS_TABLE']} where identified = %s"
    c.execute(mysql_select_query, (identified,))
    itemids = c.fetchall()
    if len(itemids) != 0:
        for id in itemids:
            ids.append(id[0])
    c.close()
    conn.close()
    return ids

def get_orders():
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select identified from {app.config['ORDERS_TABLE']}"
    c.execute(mysql_select_query)
    orders = c.fetchall()
    if len(orders) != 0:
        ret = orders
    else:
        ret = []
    c.close()
    conn.close()
    return ret

def get_items():
    results = []
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select identified, name, email, phone, address, city, payment, total from " \
                         f"{app.config['ORDERS_TABLE']} where identified = %s"
    orders = get_orders()
    for order in orders:
        quantity = []
        ids = get_order_itemid(order[0])
        for id in ids:
            quantity.append(get_name_item(id))
        c.execute(mysql_select_query, (order[0],))
        resp = c.fetchone()
        results.append({'identified': resp[0], 'name': resp[1], 'email': resp[2], 'phone': resp[3], 'address': resp[4],
                        'city': resp[5], 'payment': resp[6], 'total':resp[7], 'detail': quantity})
    c.close()
    conn.close()
    return results

def displayfunction(viewstate):
    orders = []
    user = request.cookies.get(app.config['ADMIN_USER'])
    if len(viewstate) == 0:
        try:
            orders = get_items()
        except Exception as e:
            flash('Error: {}'.format(str(e)))
            pass
    viewstate = from_python_to_js_serialization(viewstate)
    numbResults = len(orders)
    return render_template('index.html', user=user, viewstate=viewstate, results=numbResults, datas=orders)


def login_function(form):
    user_name = form.username.data
    user_pass = form.password.data
    ph = argon2.PasswordHasher()
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select password, apikey, username from {Configuration.USERS_TABLE} where username = %s LIMIT 1"
    c.execute(mysql_select_query, (user_name,))
    record = c.fetchone()
    if record is not None:
        try:
            if ph.verify(record[0], user_pass) is True:
                ret = {'apikey': record[1], 'user': record[2], 'message':'authsuccess'}
                code = 200
        except (argon2.exceptions.VerifyMismatchError, argon2.exceptions.VerificationError):
            ret = {'message': 'Login incorrect'}
            code = 401
    else:
        ret = {'message': 'Login incorrect'}
        code = 401
    c.close()
    conn.close()
    return ret, code

@app.route('/')
def root():
    resp = redirect(url_for('login'))
    return resp

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    return displayfunction(viewstate={})

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Make openapi login query with username and password
        try:
            login_systems = login_function(form)
            if login_systems[1] == 200:
                # If response is code 200 --> get apikey and set cookie
                resp = make_response(redirect("menu"))
                resp.set_cookie(key=app.config['ADMIN_USER'], value=login_systems[0]['user'], max_age=300, path='/')
            else: 
                # If response is code 401 --> redirect to error login page
                flash(f"{login_systems[0]['message']}")
                resp = render_template('login.html', form=form)
            return resp
        except Exception as e:
            flash(f"{str(e)}")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    resp = make_response(render_template('login.html', form=LoginForm(), message="Session Expired"))
    resp.set_cookie(key=app.config['ADMIN_USER'], max_age=0)
    return resp

@app.route('/admin_products', methods=['GET', 'POST'])
def admin_products():
    products = []
    images = []
    user = request.cookies.get(app.config['ADMIN_USER'])
    items = get_products()
    for product in items:
        if 'images' in product:
            if 'profile' in product['images']:
                profileimg = product['images']['profile']['path']
                bucket_name = product['images']['profile']['bucket_name']
                try:
                    file = download.download_file(profileimg, bucket_name=bucket_name)
                    product['img'] = base64.b64encode(file['data']).decode('ascii')
                    product['content_type'] = file['content_type']
                    product['profilehasimg'] = True
                except:
                    product['profilehasimg'] = False
            else:
                product['profilehasimg'] = False
            if 'images' in product['images']:
                if len(product['images']['images']) != 0:
                    for p in product['images']['images']:
                        try:
                            file = download.download_file(p['path'], p['bucket_name'])
                            img = base64.b64encode(file['data']).decode('ascii')
                            content_type = file['content_type']
                            images.append({'img': img, 'content_type': content_type, 'hasimg': True})
                        except:
                            product['hasimg'] = False
                    product['imgs'] = images
                    product['hasimg'] = True
                else:
                    product['hasimg'] = False
            product.pop('images')
        else:
            product['profilehasimg'] = False
            product['hasimg'] = False
        products.append(product)
    return render_template('admin-products.html', products=products, user=user)

@app.route('/edititem', methods=['POST'])
def edititem():
    profile = {}
    images = []
    product = get_product_by_id(request.form.get('itemid'))
    name = product['title']
    description = product['description']
    price = product['price']
    if 'images' in product:
        profile_db = product['images']
    if request.method == 'POST':
        if 'editname' in request.form:
            name = request.form.get('editname')
        if 'editdescription' in request.form:
            description = request.form.get('editdescription')
        if 'editprice' in request.form:
            price = request.form.get('editprice')
        if 'pfimg' in request.files:
            try:
                profileimg = request.files.get('pfimg')
                filepath = os.path.join(app.config['UPLOAD_PATH'], profileimg.filename)
                profileimg.save(filepath)
                resp = upload.upload_file(filepath, profileimg.content_type)
                profile['profile'] = resp
                os.remove(filepath)
            except:
                profile['profile'] = profile_db['profile']
        if 'imgs' in request.files:
            files = request.files.getlist('imgs')
            try:
                for file in files:
                    filepath = os.path.join(app.config['UPLOAD_PATH'], file.filename)
                    file.save(filepath)
                    resp = upload.upload_file(filepath, file.content_type)
                    images.append(resp)
                    os.remove(filepath)
                profile['images'] = images
            except:
                profile['images'] = profile_db['images']
        update = update_product(request.form.get('itemid'),name,description,int(price), str(profile))
        if update[1] == 200:
            flash('Updated successful')
        else:
            flash('Update item failed')
    return redirect("admin_products")

@app.route('/additem', methods=['POST'])
def additem():
    profile = {}
    images = []
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        profileimg = request.files.get('profileimg')
        filepath = os.path.join(app.config['UPLOAD_PATH'], profileimg.filename)
        profileimg.save(filepath)
        resp = upload.upload_file(filepath, profileimg.content_type)
        profile['profile'] = resp
        os.remove(filepath)
        files = request.files.getlist('files')
        for file in files:
            filepath = os.path.join(app.config['UPLOAD_PATH'], file.filename)
            file.save(filepath)
            resp = upload.upload_file(filepath, file.content_type)
            images.append(resp)
            os.remove(filepath)
        profile['images'] = images
        add = add_product(name,description,int(price),str(profile))
        if add[1] == 200:
            flash('Added successful')
        else:
            flash('Add item failed')
    return redirect("admin_products")
try:
    app.config.from_pyfile('settings.cfg')
except FileNotFoundError:
    app.config.from_object(Configuration)

upload = FileUpload(**{'api_minio_url': app.config['MINIO_API_URL'],
                       'access_key': app.config['MINIO_ACCESS_KEY'],
                       'secret_key': app.config['MINIO_SECRET_KEY'],
                       'minio_secure': app.config['MINIO_SECURE'],
                       'bucket_name':app.config['MINIO_BUCKET_NAME']})

download = FileDownload(**{'api_minio_url': app.config['MINIO_API_URL'],
                           'access_key': app.config['MINIO_ACCESS_KEY'],
                           'secret_key': app.config['MINIO_SECRET_KEY'],
                           'minio_secure': app.config['MINIO_SECURE']})

cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="admin-online",
                                                          host=app.config['HOST'],
                                                          database=app.config['DB'],
                                                          user=app.config['USERS'],
                                                          password=app.config['PASSWORD'],
                                                          port=app.config['PORT'],
                                                          pool_size=20)
if __name__ == '__main__':
    app.run()