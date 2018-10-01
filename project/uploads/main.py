from flask import Flask, request, render_template
from flask import session, redirect, url_for
from flask import g
import sqlite3, os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = './user.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        f = open('schema.sql', 'r')
        db.execute(f.read())
        db.commit()

@app.route('/')
def index():
    test_insert_user()
    if session.get('username', None) != None:
        return 'Hello %s' % session['username']
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        print(session.get('username'))
        if session.get('username', None) != None:
            return redirect(url_for('index'))
        return render_template('login.html')
    else:
        login_id = request.form.get('login_id')
        login_pw = request.form.get('login_pw')
        if login_user(login_id, login_pw):
            session['username'] = login_id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', login_failed=True)

@app.route('/login_chk', methods=['POST'])
def login_chk():
    login_id = request.form.get('login_id')
    login_pw = request.form.get('login_pw')
    print(login_id, login_pw)
    if login_user(login_id, login_pw):
        return 'true'
    else:
        return 'false'


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_user(login_id, login_pw):
    sql = "SELECT * FROM user_tbl WHERE id='{}' and pw='{}'".format(login_id, login_pw)
    db = get_db()
    res = db.execute(sql)
    res = res.fetchone()
    if res is None:
        return False
    else:
        return True

def test_insert_user():
    db = get_db()
    sql = "INSERT INTO user_tbl (id, pw) VALUES('kdh', '1234')"
    db.execute(sql)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
