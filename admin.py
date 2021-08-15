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

class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "adminonlineshopsecretkey"
    WTF_CSRF_SECRET_KEY = "adminonlineshopsecretkey"
    WTF_CSRF_TIME_LIMIT = 604800
    COOKIE = "ADMIN-ONLINE-SHOP-KEY"
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
    mysql_select_query = f"select name, email, phone, address, city, payment, total from " \
                         f"{app.config['ORDERS_TABLE']} where identified = %s"
    orders = get_orders()
    for order in orders:
        quantity = []
        ids = get_order_itemid(order[0])
        for id in ids:
            quantity.append(get_name_item(id))
        c.execute(mysql_select_query, (order[0],))
        resp = c.fetchone()
        results.append({'name': resp[0], 'email': resp[1], 'phone': resp[2], 'address': resp[3], 'city': resp[4], 'payment': resp[5],
                        'detail': quantity})
    c.close()
    conn.close()
    return results

# def displayfunction(viewstate={}):
#     if len(viewstate) == 0:



def login(form):
    user_name = form.username.data
    user_pass = form.password.data
    ph = argon2.PasswordHasher()
    conn = cnxpool.get_connection()
    c = conn.cursor()
    mysql_select_query = f"select password, apikey from {Configuration.USERS_TABLE} where username = %s LIMIT 1"
    c.execute(mysql_select_query, (user_name,))
    record = c.fetchone()
    if record is not None:
        try:
            if ph.verify(record[0], user_pass) is True:
                ret = {'apikey': record[1],'message':'authsuccess'}
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

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    results = get_items()
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Make openapi login query with username and password
        try:
            login_systems = login(form)
            if login_systems[2] == 200:
                # If response is code 200 --> get apikey and set cookie
                resp = make_response(redirect("/menu"))
            else:
                # If response is code 401 --> redirect to error login page
                flash('Login incorrect')
                resp = render_template('login.html', form=form)
            return resp
        except Exception as e:
            flash('Login incorrect')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)






try:
    app.config.from_pyfile('settings.cfg')
except FileNotFoundError:
    app.config.from_object(Configuration)
cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="admin-online",
                                                          host=app.config['HOST'],
                                                          database=app.config['DB'],
                                                          user=app.config['USERS'],
                                                          password=app.config['PASSWORD'],
                                                          port=app.config['PORT'],
                                                          pool_size=20)
if __name__ == '__main__':
    app.run()