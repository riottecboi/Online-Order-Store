from flask_env import MetaFlaskEnv
import mysql.connector
from mysql.connector import pooling
from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template, redirect, url_for, session, request, flash
import uuid
from filedownload import FileDownload
from fileupload import FileUpload
import base64
import ast
import random
import string
from datetime import timedelta

class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "xxx"
    WTF_CSRF_SECRET_KEY = "xxxx"
    WTF_CSRF_TIME_LIMIT = 604800
    COOKIE = "ONLINE-SHOP-KEY"
    HOST = "127.0.0.1"
    DB = "online-shop"
    USERS = "admin"
    PASSWORD = "xxxx"
    PORT = 3306
    ITEMS_TABLE = "items"
    ORDERS_TABLE = "orders"
    UPLOAD_TABLE = "upload"
    PRODUCTS_TABLE = "products"
    MINIO_API_URL = "xxx:9000"
    MINIO_ACCESS_KEY = "xxxx"
    MINIO_SECRET_KEY = "xxxx"
    MINIO_SECURE = False
    MINIO_BUCKET_NAME = "xxx"


app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
def list():
    lists = []
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select * from {app.config['ITEMS_TABLE']}"
    c.execute(mysql_select_query)
    items = c.fetchall()
    if len(items) != 0:
        try:
            for item in items:
                lists.append({'id': item[0], 'title': item[1], 'description': item[2], 'price': item[3], 'images': item[4]})
            ret = lists, 200
        except Exception as e:
            ret = str(e), 404
    else:
        ret = lists, 200
    c.close()
    conn.close()
    return ret

def get_items(id):
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select * from {app.config['ITEMS_TABLE']} where id=%s"
    c.execute(mysql_select_query,(id,))
    record = c.fetchone()
    if record is not None:
        ret = {'id': record[0], 'title': record[1], 'description': record[2], 'price': record[3], 'images': record[4]}, 200
    else:
        ret = {}, 404
    c.close()
    conn.close()
    return ret

def update_product(products):
    identified = str(uuid.uuid4())
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_update_query = f"insert into {app.config['PRODUCTS_TABLE']} (itemid, quantity, price, identified) values (%s,%s,%s,%s)"
    for product in products:
        c.execute(mysql_update_query,(product['id'], product['quantity'], product['price'], identified))
        conn.commit()
    c.close()
    conn.close()
    return identified

def update_order(identified, code, name, phone, email, address, city, payment, total, dayship, timeship,note):
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_update_query = f"insert into {app.config['ORDERS_TABLE']} (identified, ordercode, name, phone, email, address, city, payment, total,dayship,timeship,note) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        c.execute(mysql_update_query, (identified, code, name, phone, email, address, city, payment, total, dayship,timeship,note))
        conn.commit()
        ret = 'Updated', 200
    except Exception as e:
        ret = str(e), 404
    c.close()
    conn.close()
    return ret

@app.route('/')
def index():
    session.permanent = True
    return redirect(url_for('products'))

@app.route('/products', methods=['GET','POST'])
def products():
    items = list()
    products = []
    for product in items[0]:
        if 'images' in product:
            product['images'] = ast.literal_eval(product['images'])
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
            product.pop('images')
            products.append(product)
    return render_template('products.html', items=products), items[1]

@app.route('/detail', methods=['GET','POST'])
def detail():
    datas = []
    id_list = request.args.getlist('itemids')
    for id in id_list:
        images = []
        item = get_items(id)
        imgs = ast.literal_eval(item[0]['images'])
        for p in imgs['images']:
            try:
                file = download.download_file(p['path'], p['bucket_name'])
                img = base64.b64encode(file['data']).decode('ascii')
                content_type = file['content_type']
                images.append({'img': img, 'content_type': content_type, 'hasimg': True})
            except:
                images.append({'hasimg': False})
        item[0].pop('images')
        item[0]['imgs'] = images
        if item[1] == 200:
            datas.append(item[0])
    session['checkout'] = True
    return render_template('product-details.html', items=datas)

@app.route('/processing', methods=['GET','POST'])
def processing():
    if session.get('checkout') is not None:
        identified = request.form.get('identified')
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        city = request.form.get('city')
        type = request.form.get('type')
        note = request.form.get('message')
        total = request.form.get('price')
        date = request.form.get('dto').split('T')
        dayship = date[0]
        timeship = date[1]
        code = f"{''.join(random.choice(string.ascii_lowercase) for i in range(8))}"
        update = update_order(identified,code.upper(),name,phone,email,address,city,type,total,dayship,timeship,note)
        if update[1] == 200:
            return redirect(url_for('done', code=code.upper()))
        else:
            return redirect(url_for('products'))
    else:
        return redirect(url_for('products'))

@app.route("/done", methods=['GET'])
def done():
    code = request.args.get('code')
    flash('We receive your order and contact you soon')
    session.clear()
    return render_template("thankyou.html", code=code)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/check', methods=['POST'])
def check():
    itemids = request.form.getlist('check')
    return redirect(url_for('detail', itemids=itemids))

@app.route('/checkout', methods=['POST'])
def checkout():
    if session.get('checkout') is not None:
        final_price = 0
        products = []
        quantity = request.form.getlist('quantity')
        item_id = request.form.getlist('item')
        price = request.form.getlist('price')
        for i, q, p in zip(item_id, quantity, price):
            price = int(q)*int(p)
            final_price = final_price + price
            products.append({'id': i, 'quantity': q, 'price':p})
        identified = update_product(products)
        return render_template('checkout.html', final_price=final_price, identified=identified)
    else:
        return redirect(url_for('products'))
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
cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="online",
                                                          host=app.config['HOST'],
                                                          database=app.config['DB'],
                                                          user=app.config['USERS'],
                                                          password=app.config['PASSWORD'],
                                                          port=app.config['PORT'],
                                                          pool_size=20)
if __name__ == '__main__':
    app.run()