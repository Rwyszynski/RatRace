from sqlite3.dbapi2 import SQLITE_TRANSACTION
from flask import Flask, render_template, flash, g, url_for, redirect, session, request
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

    def verify_password(self, stored_password, provided_password):
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode(
            'utf-8'), salt.encode(ascii), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password

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

    def login_user(self):

        db = get_db()
        sql_statement = 'select id, name, email, password, is_active, is_admin from users where name=?'
        cur = db.execute(sql_statement, [self.user])
        user_record = cur.fetchone()

        if user_record != None and self.check_password(user_record['password'], self.password):
            return user_record
        else:
            self.user = None
            self.password = None
            return None


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', active_menu='login')
    else:
        user_name = '' if 'user_name' not in request.form else request.form['user_name']
        user_pass = '' if 'user_pass' not in request.form else request.form['user_pass']

        login = User(user_name, user_pass)
        login_record = login.login_user()

        if login_record != None:
            session['user'] = user_name
            flash('Login succesfull, welcome{}'.format(user_name))
            return redirect(url_for('index'))
        else:
            flash('Login failed, try again')
            return render_template('login.html')


@app.route('/logout')
def logout():

    if 'user' in session:
        session.pop('user', None)
        flash('You are logged out')
    return redirect(url_for('login'))


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


@app.route('/users')
def users():
    return 'not implemented'


@app.route('/user_status/<action>/<username>')
def user_status(action, user_name):
    return 'not implemented'


@app.route('/edit_user/<user_name>', methods=['GET', 'POST'])
def edit_user(user_name):
    return 'not implemented'


@app.route('/user_delete/<user_name>')
def delete_user(user_name):
    return 'not implemented'


@app.route('/register', methods=['GET', 'POST'])
def register():

    if not 'user' in session:
        return redirect(url_for('login'))
    login = session['user']

    db = get_db()
    message = None
    user = {}

    if request.method == 'GET':
        return render_template('register.html', active_menu='users', user=user)
    else:
        user['user_name'] = '' if not 'user_name' in request.form else request.form['user_name']
        user['email'] = '' if not 'email' in request.form else request.form['email']
        user['user_pass'] = '' if not 'user_pass' in request.form else request.form['user_pass']

        cursor = db.execute(
            'select count(*) as cnt from users where name = ?', [user['user_name']])
        record = cursor.fetchone()
        is_user_name_unique = (record['cnt'] == 0)

        cursor = db.execute(
            'select count(*) as cnt from users where email = ?', [user['email']])
        record = cursor.fetchone()
        is_user_email_unique = (record['cnt'] == 0)

        if user['user_name'] == '':
            message = 'Name cannot be empty'
        elif user['email'] == '':
            message = 'Email cannot be empty'
        elif user['user_pass'] == '':
            message = 'Password cannot be empty'
        elif not is_user_name_unique:
            message = 'User with name{} already exist'.format(
                user['user_name'])
        elif not is_user_email_unique:
            message = 'User with the email {} already exist'.format(
                user['email'])

        if not message:
            user_pass = User(user['username'], user['user_pass'])
            password_hash = user_pass.hash_password()
            sql_statement = '''insert into users(name, email, password, is_active, is_admin) values(?,?,?, True, False);'''
            db.execute(sql_statement, [
                       user['user_name'], user['email'], password_hash])
            db.commit()
            flash('User {} created'.format(message))
            return render_template('register.html', active_menu='users', user=user)
