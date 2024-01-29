from sqlite3.dbapi2 import SQLITE_TRANSACTION
from flask import Flask, render_template, flash, g, url_for, redirect
from datetime import datetime


import sqlite3
import random
import string
import hashlib
import binascii

app = Flask(__name__)

app.config['SECRET_KEY'] = 'SecretKey'

app_info = {

    'db_file': 'C:/Users/Robo/Desktop/RatRace/data/users1.db'}


def get_db():

    if not hasattr(g, 'sqlite_db'):
        conn = sqlite3.connect(app_info['db_file'])
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):

    if hasattr(g, 'sqlite3_db'):
        g.sqlite_db.close()


class User:

    def __init__(self, user='', password=''):
        self.user = user
        self.password = password

    def hash_password(self):
        os_urandom_static = b'\xb9\xed\xbev\x02v\xb1 K\x01\xf8\xb3\x04\x0b|\x975\x96\xef7\xbd\xd3\x18\xdb\xe2\x05J\xd4\x7f:\xa8\xaa\xadJ\xe8\x1bn\xea\xba\x96b\xa2\xb3\x96@\x7fJ\xdcaDgR\xe4j7\n\x82X\r\xdc'
        salt = hashlib.sha256(os_urandom_static).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac(
            'sha512', self.password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def check_password(self, stored_password, provided_password):
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode(
            'utf-8'), salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password

    def get_random_user_password(self):
        random_user = ''.join(random.choice(string.ascii_lowercase)
                              for i in range(3))
        self.user = random_user

        password_characters = string.ascii_letters
        random_password = ''.join(random.choice(
            password_characters)for i in range(3))
        self.password = random_password


@app.route('/init_app')
def init_app():
    db = get_db()
    sql_statement = 'select count(*) as cnt from users where is_active and is_admin'
    cur = db.execute(sql_statement)
    active_admins = cur.fetchone()

    if active_admins != None and active_admins['cnt'] > 0:
        flash('Application is already setup')
        return redirect(url_for('index'))

    user_pass = User()
    user_pass.get_random_user_password()
    sql_statement = ''' insert into users (name, email, password, is_active, is_admin) values(?,?,?,True, True);'''
    db.execute(sql_statement, [user_pass.user,
               'robo@cool.pl', user_pass.hash_password()])
    db.commit()
    flash('user {} with password {} has been created'.format(
        user_pass.user, user_pass.password))
    return redirect(url_for('index'))


@app.route('/')
def index():

    while True:

        teraz = datetime.now()
        times = teraz.strftime('%H:%M:%S')
        return render_template('index.html', times=times)
        teraz.sleep(1)


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/rewards')
def rewards():
    return render_template('rewards.html')


@app.route('/access')
def access():
    return render_template('access.html')


@app.route('/login')
def login():
    return render_template('login.html')
