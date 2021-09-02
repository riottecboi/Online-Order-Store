import json
import mysql.connector
from argon2 import PasswordHasher
import uuid
from datetime import datetime
cfg = dict(mysql_conn_cfg={
    "host": "127.0.0.1",
    "db": "online-shop",
    "user": "admin",
    "password": "thisisasecretkey",
    "port": 3306
}, table="users")


def insert_to_user_table(cnn_cfg, table, user_name, user_pass, dl_name, enable=True):
    conn = mysql.connector.connect(host=cnn_cfg['host'],
                                   database=cnn_cfg['db'],
                                   user=cnn_cfg['user'],
                                   password=cnn_cfg['password'],
                                   port=cnn_cfg['port'])
    c = conn.cursor()
    ph = PasswordHasher()
    mysql_insert_query = f"""INSERT INTO {table} (username, password, displayname, enable)
                                        VALUES (%s, %s, %s, %s) """
    mysql_record_tuple = (user_name, ph.hash(user_pass),dl_name, enable)
    c.execute(mysql_insert_query, mysql_record_tuple)
    conn.commit()
    c.close()
    conn.close()


insert_to_user_table(cfg['mysql_conn_cfg'], cfg['table'], user_name='test1', user_pass='test1', dl_name='test1')
#insert_to_user_table(cfg['mysql_conn_cfg'], cfg['table'], user_name='test1', user_pass='test1', dl_name='test1', login=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#insert_to_user_table(cfg['mysql_conn_cfg'], cfg['table'], user_name='test3', user_pass='test3')
