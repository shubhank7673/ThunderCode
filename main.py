from flask import Flask,render_template,request,session,redirect
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#from flask_mail import Mail,Message
import os
import json
from sqlite3 import *
from werkzeug import secure_filename
import math

with open('config.json','r') as c:
    params = json.load(c)["params"]

# method to host using the local server or production server and xampp with sqlalchemy,mysql,apacheserver
# but we will go with sqlite database hence this section is commented
'''if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri'] #for local server
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri'] #for production server

db = SQLAlchemy(app)
'''

conn = Connection("database.db")
cur = conn.cursor()
cur.execute("create table if not exists contact(sno integer primary key AUTOINCREMENT,name text,email varchar(20),phone varchar(20),message text,date varchar(20))")
cur.execute("create table if not exists posts(sno integer primary key AUTOINCREMENT,title text,content text,date varchar(20),slug varchar(50),img_file varchar(20),sub_heading text)")
conn.commit()
conn.close()

app = Flask(__name__)
app.secret_key = 'This is secret key'

app.config['UPLOAD_FOLDER'] = params['upload_location']

@app.route("/")
def home():

    if('user' in session and session['user']=='DummyUser'):
        params['is_logged_in']="yes"
    else:
        params['is_logged_in']="no"
    conn = Connection('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts order by date desc;")
    #LIMIT 5
    posts = cur.fetchall()
    conn.close()
    # 5 in the number of posts per page it can be changed accordingly
    last = math.ceil(len(posts)/2)
    page = request.args.get('page')
    if(not str(page).isdigit()):
        page = 1
    page = int(page)
    #slicing posts according to the number of posts per page
    posts = posts[(page-1)*2:(page-1)*2+2]
    if(page==1):
        prev="#"
        next = "/?page="+str(page+1)
    elif(page==last):
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)

    return render_template('index.html',params=params,posts=posts,prev=prev,next=next)


@app.route("/totalposts")
def totalposts():
    if('user' in session and session['user']=='DummyUser'):
        params['is_logged_in']="yes"
    else:
        params['is_logged_in']="no"
    conn = Connection('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts order by date desc;")
    #LIMIT 2
    posts = cur.fetchall()
    conn.close()
    # 2 in the number of posts per page it can be changed accordingly
    last = math.ceil(len(posts)/2)
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    #slicing posts according to the number of posts per page
    posts = posts[(page-1)*2:(page-1)*2+2]
    if(page==1):
        prev="#"
        next = "/?page="+str(page+1)
    elif(page==last):
        prev = "/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)

    return render_template('totalposts.html',params=params,posts=posts,prev=prev,next=next)


@app.route('/about')
def about():
    if('user' in session and session['user']=='DummyUser'):
        params['is_logged_in']="yes"
    else:
        params['is_logged_in']="no"
    return render_template('about.html',params=params)

@app.route('/profile')
def profile():
    if('user' in session and session['user']=='DummyUser'):
        params['is_logged_in']="yes"
    else:
        params['is_logged_in']="no"
    return render_template('profile.html',params=params)

@app.route('/post/<string:post_slug>',methods=['GET'])
def postf(post_slug):
    if('user' in session and session['user']=='DummyUser'):
        params['is_logged_in']="yes"
    else:
        params['is_logged_in']="no"
    conn = Connection('database.db')
    cur = conn.cursor()
    cur.execute("select * from posts where slug = ?",(post_slug,))
    post = cur.fetchone()
    conn.close()
    return render_template('post.html',params=params,post=post)
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')

@app.route('/delete/<string:sno>',methods=['GET','POST'])
def delete(sno):
    if('user' in session and session['user']=='DummyUser'):
        conn = Connection('database.db')
        cur = conn.cursor()
        cur.execute("delete from posts where sno= ?",(sno,))
        conn.commit()
        cur.execute("select * from posts")
        posts = cur.fetchall()
        conn.close()
        params['is_logged_in']="yes"
        return render_template('dashboard.html',params=params,posts=posts)
    else :
        return "<h1>login first</h1>"
@app.route('/edit/<string:sno>',methods=['GET','POST'])
def edit(sno):
    if('user' in session and session['user']=='DummyUser'):
        params['is_logged_in']="yes"
        if request.method=='POST':
            title = request.form.get('title')
            subheading = request.form.get('subheading')
            slug = request.form.get('slug')
            img_file = request.form.get('img_file')
            content = request.form.get('content')
            if sno=='0':
                conn = Connection('database.db')
                cur = conn.cursor()
                cur.execute("select sno from posts order by sno desc")
                x = cur.fetchone()
                id = x[0]+1
                cur.execute("insert into posts values(?,?,?,?,?,?,?)",(id,title,content,datetime.datetime.now(),slug,img_file,subheading))
                conn.commit()
                conn.close()
            else:
                conn = Connection('database.db')
                cur = conn.cursor()
                id = int(sno)
                cur.execute("UPDATE posts set title= ?,content= ?,date= ?,slug= ?,img_file= ?,sub_heading= ? where sno = ?",(title,content,datetime.datetime.now(),slug,img_file,subheading,sno))
                conn.commit()
                conn.close()
                return redirect('edit/'+str(id))
    conn = Connection('database.db')
    cur = conn.cursor()
    cur.execute("select * from posts where sno = ?",(sno,))
    x = cur.fetchone()
    return render_template('Edit.html',params=params,post = x,sno = sno)
@app.route('/dashboard',methods=['GET','POST'])
def login():
    conn = Connection('database.db')
    cur = conn.cursor()
    cur.execute("select * from posts")
    posts = cur.fetchall()
    conn.close()
    if('user' in session and session['user']=='DummyUser'):
        params['is_logged_in']="yes"
        return render_template('dashboard.html',params=params,posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if username=='DummyUser' and password=='DummyPassword':
            session['user'] = username
            params['is_logged_in']="yes"
            return render_template('dashboard.html',params=params,posts=posts)
    else:
        return render_template('signin.html',params=params)

@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if('user' in session and session['user']=='DummyUser'):
        if request.method == 'POST':
            file = request.files['file1']
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
            return "uploaded successfully"
@app.route("/contact",methods=['GET','POST'])
def contact():
    if('user' in session and session['user']=='DummyUser'):
        params['is_logged_in']="yes"
    else:
        params['is_logged_in']="no"
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        conn = Connection('database.db')
        cur = conn.cursor()
        cur.execute("select sno from contact order by sno desc")
        x = cur.fetchone()
        id = x[0]+1
        cur.execute("insert into contact values(?,?,?,?,?,?)",(id,name,email,phone,message,str(datetime.datetime.now())))
        conn.commit()
        conn.close()
        return render_template('contact.html',params=params)
    else:
        return render_template('contact.html',params=params)
app.run(debug=True)
