from typing import Any
from flask import Flask
from flask import redirect, render_template, request, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import sql
from sqlalchemy.sql.elements import Null
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import logging
import sys
from sqlalchemy.exc import IntegrityError



app = Flask(__name__)
app.secret_key = "salattu"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://jtrbebwzyskmln:53f8e7c7e4f65fe9ca30ff1741dccfc1d95f46aaeb761b1c38f0a19217d64e1a@ec2-54-155-87-214.eu-west-1.compute.amazonaws.com:5432/dcbo0o6er550eq"


db = SQLAlchemy(app)

@app.route("/")
def index():
    
    admin_rights = '0'

    if 'username' in session:

        username = session["username"]

        result = db.session.execute("SELECT admin_rights FROM users WHERE username =:username", {'username':username})
        admin_rights = str(result.fetchone())
        
        if len(admin_rights) > 0:
            
            admin_rights = admin_rights.strip(",'()")
        else:
            admin_rights = '0'
    

    #if session["username"] != None and session["username"] in admins:

     #   admin_rights = True

    id_num = 1
    message_list = []
    result = db.session.execute("SELECT COUNT(*) FROM forums")
    count = result.fetchone()[0]
    result = db.session.execute("SELECT content, forum_id FROM messages")
    messages = result.fetchall()

    for i in range(count+1):

        j = 0

        for message in messages:

            if message[1] == i:

                j += 1
        message_list.append(j)     

    result = db.session.execute("SELECT subject, id, username, sent_at FROM forums")
    forums = result.fetchall()

    secret_forums = None

    if 'username' in session:

        result = db.session.execute("SELECT * From secret_forums WHERE :username = ANY(users)", {"username":username})
        
        secret_forums = result.fetchall()

    result = db.session.execute("SELECT content, message_id FROM comments")
    comments = result.fetchall()

    return render_template("index.html", count=count, forums=forums, message_list=message_list, session = session, id_num = id_num, admin_rights = admin_rights, secret_forums = secret_forums) 


@app.route("/forum/<int:forum_id>")
def forum(forum_id):
    id_num = 1
    comment_list = []
    result = db.session.execute("SELECT COUNT(*) FROM messages")
    count = result.fetchone()[0]
    result = db.session.execute("SELECT content, id, username, sent_at FROM messages WHERE forum_id=:forum_id Group By id", {"forum_id":forum_id})
    messages = result.fetchall()
    result = db.session.execute("SELECT id, content, username, sent_at, message_id, forum_id FROM comments WHERE forum_id=:forum_id GROUP BY id", {"forum_id":forum_id})
    comments = result.fetchall()
    args = (request.view_args)
    print('Hello world!', file=sys.stderr)


    return render_template("forum.html", count=count, messages=messages, comments=comments, session = session, id_num = id_num, forum_id = forum_id, args = args) 

@app.route("/secret_forum/<int:forum_id>")
def secret_forum(forum_id):
    id_num = 1
    comment_list = []
    result = db.session.execute("SELECT COUNT(*) FROM secret_messages")
    count = result.fetchone()[0]
    result = db.session.execute("SELECT content, id, username, sent_at FROM secret_messages WHERE forum_id=:forum_id Group By id", {"forum_id":forum_id})
    messages = result.fetchall()
    result = db.session.execute("SELECT id, content, username, sent_at, message_id, forum_id FROM secret_comments WHERE forum_id=:forum_id GROUP BY id", {"forum_id":forum_id})
    comments = result.fetchall()
    args = (request.view_args)
    print('Hello world!', file=sys.stderr)


    return render_template("secret_forum.html", count=count, messages=messages, comments=comments, session = session, id_num = id_num, forum_id = forum_id, args = args) 

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # TODO: check username and password
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_password = result.fetchone()
    user_password = str(user_password)
    user_password = user_password.strip(",'()")  
    #print(user)  
    if user_password == None:
        # TODO: invalid username
           
        return redirect("/")
    else:
        if password == str(user_password):

            session["username"] = username
            #session.username = username
            return redirect("/")



        else:
            # TODO: invalid password
            #print(user)
            #app.logger.info(user)
            #print('Hello world!', file=sys.stderr)
            flash('väärä salasana')
            
            return redirect("/")


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/new_user", methods = ["POST"])
def new_user():

    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    result = db.session.execute('SELECT username FROM users')
    users = result.fetchall()

    print('Käyttäjä jo olemassa', file=sys.stderr)



    if username in users:

        flash('Käyttäjänimi on jo käytössä')

        return redirect("/")

    elif password1 == password2 and len(password1) > 0:

        sql = "Insert Into users (username, password) Values (:username, :password1)"
        
        try:
            db.session.execute(sql, {"username":username,"password1": password1})
        
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Käyttäjä otettu')
            return redirect("/")

        return redirect("/")
    else:

        return redirect("/register")


@app.route("/new_forum")
def new_forum():
    return render_template("new_forum.html")


@app.route("/add_forum", methods=["POST"])
def add_forum():
    content = request.form["content"]
    user = session["username"]
    sent_at = datetime.now().replace(second=0, microsecond=0)
    sql = "INSERT INTO forums (subject, username, sent_at) VALUES (:content,:user,:sent_at)"
    db.session.execute(sql, {"content":content,"user":user,"sent_at":sent_at})
    db.session.commit()
    return redirect("/")

@app.route("/new")
def new():
    args = request.view_args
    return render_template("new.html",args =args)

@app.route("/send_message", methods=["POST"])
def send():
    content = request.form["content"]
    kayttaja = session["username"]
    aika = datetime.now().replace(second=0, microsecond=0)
    forum_id = request.form['forum_id']
    
    if len(content) > 100:
        error = 'Liian pitkä viesti'
        return rendertemplate("index.html", error = error)
    
    sql = "INSERT INTO messages (content, username, sent_at, forum_id) VALUES (:content,:kayttaja,:aika,:forum_id)"
    db.session.execute(sql, {"content":content,"kayttaja":kayttaja,"aika":aika,'forum_id':forum_id})
    db.session.commit()
    return redirect("/")

@app.route("/send_secret_message", methods=["POST"])
def send_secret_message():
    content = request.form["content"]
    kayttaja = session["username"]
    aika = datetime.now().replace(second=0, microsecond=0)
    forum_id = request.form['forum_id']
    sql = "INSERT INTO secret_messages (content, username, sent_at, forum_id) VALUES (:content,:kayttaja,:aika,:forum_id)"
    db.session.execute(sql, {"content":content,"kayttaja":kayttaja,"aika":aika,'forum_id':forum_id})
    db.session.commit()
    return redirect("/")


@app.route("/comment/<int:id_num>/<int:forum_id>")
def comment(id_num, forum_id):
    return render_template("comment.html",id_num =id_num, forum_id=forum_id)

@app.route("/secret_comment/<int:id_num>/<int:forum_id>")
def secret_comment(id_num, forum_id):
    return render_template("secret_comment.html",id_num =id_num, forum_id=forum_id)


@app.route("/send_comment", methods=["POST"])
def send_comment():
    content = request.form["content"]
    message_id = request.form["id_num"]
    forum_id = request.form["forum_id"]
    username = session["username"]
    sent_at = datetime.now().replace(second=0, microsecond=0)
    
    if len(content) > 200:
        error = 'Liian pitkä viesti'
        return rendertemplate("index.html", error = error)
    sql = "INSERT INTO comments (content,message_id,forum_id,username,sent_at) VALUES (:content,:message_id,:forum_id, :username, :sent_at)"
    db.session.execute(sql, {"content":content, "message_id":message_id, "forum_id":forum_id, "username":username,"sent_at":sent_at})
    db.session.commit()
    return redirect("/")

@app.route("/send_secret_comment", methods=["POST"])
def send_secret_comment():
    content = request.form["content"]
    message_id = request.form["id_num"]
    forum_id = request.form["forum_id"]
    username = session["username"]
    sent_at = datetime.now().replace(second=0, microsecond=0)
    sql = "INSERT INTO secret_comments (content,message_id,forum_id,username,sent_at) VALUES (:content,:message_id,:forum_id, :username, :sent_at)"
    db.session.execute(sql, {"content":content, "message_id":message_id, "forum_id":forum_id, "username":username,"sent_at":sent_at})
    db.session.commit()
    return redirect("/")

@app.route("/edit_message/<int:id_num>/<content>")
def edit_message(id_num,content):
    username = session["username"]
    sql = "SELECT 1 FROM messages WHERE id =:id_num and username =:username"
    result = db.session.execute(sql,{"id_num":id_num, "username":username})
    rights = result.fetchone()
    
    if rights != None:
        return render_template("edit_comment.html", id_num = id_num, content = content)
    else:
        flash("Ei sallitua")
        error = 'Ei sallittua'
        return redirect(url_for('index', error = error))
    return render_template("edit_message.html",id_num = id_num)

@app.route("/edit_secret_message/<int:id_num>/<content>")
def edit_secret_message(id_num, content):
    username = session["username"]
    sql = "SELECT 1 FROM secret_messages WHERE id =:id_num and username =:username"
    result = db.session.execute(sql,{"id_num":id_num, "username":username})
    rights = result.fetchone()
    
    if rights != None:
        return render_template("edit_secret_message.html", id_num = id_num, content = content)
    else:
        error = 'Ei sallittua'
        return redirect(url_for('index', error = error))
    return render_template("edit_secret_message.html",id_num = id_num)

@app.route("/edit_comment/<int:id_num>/<content>") 
def edit_comment(id_num, content):
    username = session["username"]
    sql = "SELECT 1 FROM comments WHERE id =:id_num and username =:username"
    result = db.session.execute(sql,{"id_num":id_num, "username":username})
    rights = result.fetchone()
    
    if rights != None:
        return render_template("edit_comment.html", id_num = id_num, content = content)
    else:
        error = 'Ei sallittua'
        return redirect(url_for('index', error = error))

@app.route("/edit_secret_comment/<int:id_num>/<content>") 
def edit_secret_comment(id_num, content):
    username = session["username"]
    sql = "SELECT 1 FROM secret_comments WHERE id =:id_num and username =:username"
    result = db.session.execute(sql,{"id_num":id_num, "username":username})
    rights = result.fetchone()
    
    if rights != None:
        return render_template("edit_secret_comment.html", id_num = id_num, content = content)
    else:
        error = 'Ei sallittua'
        return redirect(url_for('index', error = error))
    return render_template("edit_secret_comment.html", id_num = id_num)

@app.route("/update_message", methods=["POST"])
def update_message():
    content = request.form["content"]
    id_num = request.form["id_num"]
    
    sql = "UPDATE messages Set content = :content Where id =:id_num"
    db.session.execute(sql, {"content":content, "id_num":id_num})
    db.session.commit()
    return redirect("/")

@app.route("/update_secret_message", methods=["POST"])
def update_secret_message():
    content = request.form["content"]
    id_num = request.form["id_num"]
  
    sql = "UPDATE secret_messages Set content = :content Where id =:id_num"
    db.session.execute(sql, {"content":content, "id_num":id_num})
    db.session.commit()
    return redirect("/")

@app.route("/update_comment", methods=["POST"])
def update_comment():
    content = request.form["content"]
    id_num = request.form["id_num"]
    
    sql = "UPDATE comments Set content = :content Where id =:id_num"
    db.session.execute(sql, {"content":content, "id_num":id_num})
    db.session.commit()
    return redirect("/")

@app.route("/update_secret_comment", methods=["POST"])
def update_secret_comment():
    content = request.form["content"]
    id_num = request.form["id_num"]
   
    sql = "UPDATE secret_comments Set content = :content Where id =:id_num and forum_id = :forum_id"
    db.session.execute(sql, {"content":content, "id_num":id_num, "forum_id":forum_id})
    db.session.commit()
    return redirect("/")



@app.route("/delete_message/<int:id_num>")
def delete_message(id_num):
        
    sql = "DELETE From messages WHERE id = :id_num"
    sql2 = "Delete From comments Where message_id = :id_num"
    db.session.execute(sql, {"id_num":id_num})
    db.session.commit()

    db.session.execute(sql2, {"id_num":id_num})

    db.session.commit()

    return redirect("/")

@app.route("/delete_secret_message/<int:id_num>")
def delete_secret_message(id_num):
    
    sql = "DELETE From secret_messages WHERE id = :id_num"
    sql2 = "Delete From secret_comments Where message_id = :id_num"
    db.session.execute(sql, {"id_num":id_num})
    db.session.commit()

    db.session.execute(sql2, {"id_num":id_num})

    db.session.commit()

    return redirect("/")


@app.route("/delete_comment/<int:id_num>")
def delete_comment(id_num):
    
    sql = "DELETE From comments WHERE id = :id_num"

    db.session.execute(sql, {"id_num":id_num})
    db.session.commit()

    return redirect("/")


@app.route("/delete_secret_comment/<int:id_num>")
def delete_secret_comment(id_num):
    
    sql = "DELETE From secret_comments WHERE id = :id_num"

    db.session.execute(sql, {"id_num":id_num})
    db.session.commit()

    return redirect("/")

@app.route("/delete_forum/<int:id_num>")
def delete_forum(id_num):
    
    sql = "DELETE From forums WHERE id = :id_num"
    sql2 = "DELETE From messages WHERE forum_id = :id_num"
    sql3 = "DELETE From comments WHERE forum_id = :id_num"


    db.session.execute(sql, {"id_num":id_num})
    db.session.commit()

    db.session.execute(sql2, {"id_num":id_num})
    db.session.commit()

    db.session.execute(sql3, {"id_num":id_num})
    db.session.commit()

    return redirect("/")

@app.route("/delete_secret_forum/<int:id_num>")
def delete_secret_forum(id_num):
    
    sql = "DELETE From secret_forums WHERE id = :id_num"
    sql2 = "DELETE From secret_messages WHERE forum_id = :id_num"
    sql3 = "DELETE From secret_comments WHERE forum_id = :id_num"


    db.session.execute(sql, {"id_num":id_num})
    db.session.commit()

    db.session.execute(sql2, {"id_num":id_num})
    db.session.commit()

    db.session.execute(sql3, {"id_num":id_num})
    db.session.commit()

    return redirect("/")



@app.route("/search", methods=["POST"])
def search():

    s_word = request.form["content"]
    
    s = str.strip(s_word,"'")

    username = session["username"]

    sql = "UPDATE users Set s_word = :s_word Where username = :username"

    db.session.execute(sql, {"username":username, "s_word":s_word})
    db.session.commit()

    result = db.session.execute("SELECT messages.content, users.s_word from messages, users Where users.username = :username and messages.content LIKE  '%' || users.s_word  || '%'"  ,{"username":username, "s_word":s_word})

    messages = result.fetchall()
    db.session.commit()

    result = db.session.execute("SELECT comments.content, users.s_word from comments, users Where users.username = :username and comments.content LIKE '%' || users.s_word || '%'",{"username":username, "s_word":s_word})


    comments = result.fetchall()
    db.session.commit()

    return render_template("/search_results.html", messages = messages, comments = comments)

