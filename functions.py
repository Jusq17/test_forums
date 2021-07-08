from db import db

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # TODO: check username and password
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_password = result.fetchone()
    
    hash_value = user_password[0]
    
    if user_password == None:
        flash('Käyttäjää ei ole olemassa')
        return redirect("/")
    else:
        if check_password_hash(hash_value, password):
            
            session['username'] = username
            return redirect("/")
        else:
            flash('Väärä salasana')
            return redirect('/')
          
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")
  
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
        
        password = generate_password_hash(password1)

        sql = "Insert Into users (username, password) Values (:username, :password)"
        
        try:
            db.session.execute(sql, {"username":username,"password": password})
        
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Käyttäjä otettu')
            return redirect("/")

        return redirect("/")
    else:

        return redirect("/register")
      
@app.route("/add_forum", methods=["POST"])
def add_forum():
    content = request.form["content"]
    user = session["username"]
    sent_at = datetime.now().replace(second=0, microsecond=0)
    sql = "INSERT INTO forums (subject, username, sent_at) VALUES (:content,:user,:sent_at)"
    db.session.execute(sql, {"content":content,"user":user,"sent_at":sent_at})
    db.session.commit()
    return redirect("/")

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
   
    sql = "UPDATE secret_comments Set content = :content Where id =:id_num"
    db.session.execute(sql, {"content":content, "id_num":id_num})
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
