# -*- coding: utf-8 -*-
from flask import Flask,session,g,render_template,request,redirect,url_for,escape
import sqlite3
import hashlib
from werkzeug import secure_filename


app = Flask(__name__)
DATABASE = './test.db'
app.secret_key = 'a'

def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db
def init_db():
    with app.app_context():
        db = get_db()
        f=open('schema.sql','r')
        db.execute(f.read())
        db.commit()

def add_user(user_email,user_pw,user_nick,user_phone):
    pw = hashlib.sha224(b"user_pw").hexdigest()
    sql = 'insert into users(user_email,user_pw,user_nick,user_phone) values("{}","{}","{}","{}")'.format(user_email,pw,user_nick,user_phone)
    db = get_db()
    db.execute(sql)
    db.commit()

def get_user(user_email,user_pw):
    pw = hashlib.sha224(b"user_pw").hexdigest()
    sql = 'select * from users where user_email="{}" and user_pw="{}"'.format(user_email,pw)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def update_user(user_pw,user_nick,user_phone,user_email):
    pw = hashlib.sha224(b"user_pw").hexdigest()
    sql = 'update users set user_pw="{}",user_nick="{}",user_phone="{}" where user_email="{}"'.format(pw,user_nick,user_phone,user_email)
    db = get_db()
    db.execute(sql)
    db.commit()

def find_user_info(user_email):
    sql = 'select * from users where user_email="{}"'.format(user_email)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def del_user(user_email):
    sql = 'delete from users where user_email="{}"'.format(user_email)
    db = get_db()
    db.execute(sql)
    db.commit()
    return ''

def add_board(title,text,writer,_file):
    sql = 'insert into board(title,text,writer,_file) values("{}","{}","{}","{}")'.format(title,text,writer,_file)
    db =get_db()
    db.execute(sql)
    res = db.commit()
    return res

def show_all():
    sql = 'select idx,title,writer,dt from board'
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

def get_nick(user_email):
    sql = 'select user_nick from users where user_email="{}"'.format(user_email)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res
def get_view(idx):
    sql = 'select * from board where idx="{}"'.format(idx)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res
def board_editt(idx,title,contents):
    sql = 'update board set title="{}",text="{}" where idx="{}"'.format(title,contents,idx)
    db = get_db()
    db.execute(sql)
    db.commit()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if 'user_email' in session:
            res = find_user_info(escape(session['user_email']))
            return render_template('jisub.html',data=res)
        else:
            return render_template('login.html')
        #return redirect(url_for('index'))
    else:
        user_email = request.form.get('user_email')
        user_pw = request.form.get('user_pw')
        ok = get_user(user_email,user_pw)
        if ok:
            session['user_email'] = user_email
            return render_template('jisub.html',data=ok)
        else:
            return redirect(url_for('index'))
@app.route('/join',methods=['GET','POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')
    else:
        user_email = request.form.get('user_email')
        user_pw = request.form.get('user_pw')
        user_nick = request.form.get('user_nick')
        user_phone = request.form.get('user_phone')
        add_user(user_email,user_pw,user_nick,user_phone)
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.pop('user_email',None)
    return redirect(url_for('index'))

@app.route('/edit',methods=['GET','POST'])
def edit():
    if request.method == 'GET':
        if 'user_email' in session:
            res = find_user_info(escape(session['user_email']))
            return render_template('edit.html',data=res)
        else:
            return "fucking man~"
    else:
        if 'user_email' in session:
            user_pw = request.form.get('user_pw')
            user_nick = request.form.get('user_nick')
            user_phone = request.form.get('user_phone')
            update_user(user_pw,user_nick,user_phone,escape(session['user_email']))
            res = find_user_info(escape(session['user_email']))
            return redirect(url_for('index'))
        else:
            return "꺼저"

@app.route('/delete')
def del_users():
    if 'user_email' in session:
        del_user(escape(session['user_email']))
        return redirect(url_for('index'))
    else:
        return 'Error'

@app.route('/board',methods=['GET'])
def board():
    if 'user_email' in session:
        res = show_all()
        return render_template('board.html', data=res)
    else:
        return redirect(url_for('login'))

@app.route('/board_write',methods=['GET','POST'])
def board_write():
    if request.method == 'GET':
        if 'user_email' in session:
            #res = get_nick(escape(session['user_email']))
            res = get_nick(escape(session['user_email']))
            return render_template('board_write.html',data=res)
        else:
            return redirect(url_for('index'))
    else:
        if 'user_email' in session :
            title = request.form.get('title')
            contents = request.form.get('contents')
            _file = request.files['_file']
            res = get_nick(escape(session['user_email']))
            if _file:
                _file.save('./uploads/'+secure_filename(_file.filename))
                add_board(title,contents,res[0][0],_file)
                return redirect(url_for('board'))
            else:
                add_board(title,contents,res[0][0],_file)
                return redirect(url_for('board'))
        else: return redirect(url_for('index'))
@app.route('/board/<idx>',methods=['GET','POST'])
def board_view(idx):
    if request.method=='GET':
        if 'user_email' in session:
            res = get_view(idx)
            res2 = board_reply_get(idx)
            return render_template('board_view.html',data=res,data2=res2)
        else: return redirect(url_for('index'))
    else:
        re = request.form.get('reply')
        nick = get_nick(escape(session['user_email']))
        board_reply_save(idx,re,nick[0][0])
        return redirect(url_for('board_view',idx=idx))

@app.route('/board_edit/<idx>',methods=['GET','POST'])
def board_edit(idx):
    if request.method == 'GET':
        if 'user_email' in session:
            rt = get_nick(escape(session['user_email']))
            res = ghkrdls(idx,rt[0][0])
            if res:
                return render_template('board_edit.html',data=res)
            else: return redirect(url_for('board'))
        else: return redirect(url_for('index'))
    else:
        ed_title = request.form.get('title')
        ed_contents = request.form.get('contents')
        board_editt(idx,ed_title,ed_contents)
        return redirect(url_for('board'))
@app.route('/board_del/<idx>')
def board_del(idx):
    if 'user_email' in session:
        rt = get_nick(escape(session['user_email']))
        res = ghkrdls(idx,rt[0][0])
        res2 = board_reply_get(idx)
        if res:
            board_dell(idx)
            return redirect(url_for('board'))
        else:return "<script>alert('삭제권한없음');history.back()</script>"
    else: redirect(url_for('index'))


def ghkrdls(idx,nick):
    sql = 'select idx,title,text,writer,_file from board where idx="{}" and writer="{}"'.format(idx,nick)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res
def board_dell(idx):
    sql = 'delete from board where idx={}'.format(idx)
    db = get_db()
    db.execute(sql)
    db.commit()

def board_reply_save(idx2,text,writer):
    sql = 'insert into board_reply(idx2,text,writer) values("{}","{}","{}")'.format(idx2,text,writer)
    db = get_db()
    db.execute(sql)
    db.commit()
def board_reply_get2(idx):
    sql= 'select idx2,text,writer from board_reply where idx="{}"'.format(idx)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

def board_reply_get(idx):
    sql = 'select text,writer,dt from board_reply where idx2="{}"'.format(idx)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    rv.close()
    return res

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8889)


