from app import app
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

@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/new_forum")
def new_forum():
    return render_template("new_forum.html")


@app.route("/new")
def new():
    args = request.view_args
    return render_template("new.html",args =args)


@app.route("/comment/<int:id_num>/<int:forum_id>")
def comment(id_num, forum_id):
    return render_template("comment.html",id_num =id_num, forum_id=forum_id)

@app.route("/secret_comment/<int:id_num>/<int:forum_id>")
def secret_comment(id_num, forum_id):
    return render_template("secret_comment.html",id_num =id_num, forum_id=forum_id)
  
@app.route("/edit_message/<int:id_num>/<content>")
def edit_message(id_num,content):
    username = session["username"]
    sql = "SELECT 1 FROM messages WHERE id =:id_num and username =:username"
    result = db.session.execute(sql,{"id_num":id_num, "username":username})
    rights = result.fetchone()
    
    if rights != None:
        return render_template("edit_message.html", id_num = id_num, content = content)
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

