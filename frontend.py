from flask_env import MetaFlaskEnv
import mysql.connector
from mysql.connector import pooling
from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template, redirect, url_for, make_response, request

class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "onlineshopsecretkey"
    WTF_CSRF_SECRET_KEY = "onlineshopsecretkey"
    WTF_CSRF_TIME_LIMIT = 604800
    COOKIE = "ONLINE-SHOP-KEY"
    HOST = "127.0.0.1"
    DB = "online-shop"
    USERS = "admin"
    PASSWORD = "thisisasecretkey"
    PORT = 3306
    ITEMS_TABLE = "items"
    ORDERS_TABLE = "orders"
    UPLOAD_TABLE = "upload"

app = Flask(__name__)
csrf = CSRFProtect(app)

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
                lists.append({'id': item[0], 'title': item[1], 'description': item[2], 'price': item[3]})
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
        ret = {'id': record[0], 'title': record[1], 'description': record[2], 'price': record[3]}, 200
    else:
        ret = {}, 404
    return ret

@app.route('/')
def index():
    return redirect(url_for('products'))

@app.route('/products', methods=['GET','POST'])
def products():
    items = list()
    return render_template('products.html', items=items[0]), items[1]

@app.route('/detail', methods=['GET','POST'])
def detail():
    datas = []
    id_list = request.args.getlist('itemids')
    for id in id_list:
        item = get_items(id)
        if item[1] == 200:
            datas.append(item[0])
    return render_template('product-details.html', items=datas)


@app.route('/check', methods=['POST'])
def check():
    itemids = request.form.getlist('check')
    return redirect(url_for('detail', itemids=itemids))

@app.route('/processing', methods=['POST'])
def processing():
    products = []
    quantity = request.form.getlist('quantity')
    item_id = request.form.getlist('item')
    for i, q in zip(item_id, quantity):
        products.append({'id': i, 'quantity': q})
    return redirect(url_for('checkout', products=products))

try:
    app.config.from_pyfile('settings.cfg')
except FileNotFoundError:
    app.config.from_object(Configuration)
cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="online",
                                                          host=app.config['HOST'],
                                                          database=app.config['DB'],
                                                          user=app.config['USERS'],
                                                          password=app.config['PASSWORD'],
                                                          port=app.config['PORT'],
                                                          pool_size=20)
if __name__ == '__main__':
    app.run()