from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from app import app, get_db


@app.route('/join', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        # print(request.form)
        form = request.form

        db = get_db()
        sql = """INSERT INTO `users` ( `email`, `fname`, `lname`, `password`)
                VALUES (%s, %s, %s, %s)"""
        cursor = db.cursor()
        cursor.execute(sql, (form['email'],
                             form['fname'],
                             form['lname'],
                             form['password']
                             ))

        flash('New Account Created')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        sql = "SELECT id, email, password from users where email= %s and password= %s limit 1"
        db = get_db()
        cursor = db.cursor()
        cursor.execute(sql, (request.form['email'], request.form['password']))
        if cursor.rowcount:
            session['logged_in'] = True
            session['user_id'] = cursor.fetchone()['id']
            flash('You were logged in')
            sql = "UPDATE users set login=CURRENT_TIMESTAMP where id= %s"
            cursor.execute(sql, (session['user_id'], ))
            return redirect(url_for('create_thread'))
        else:
            flash('Invalid Username or password')
            error = 'Invalid Username or password'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/threads/<int:threads_id>')
def show_thread(threads_id):

    db = get_db()
    sql = "SELECT * from comments join users on comments.users_id=users.id where threads_id= %s"
    cursor = db.cursor()
    cursor.execute(sql, (int(threads_id),))
    comments = cursor.fetchall()
    print(comments)
    sql = "SELECT * from threads where id= %s limit 1"
    cursor.execute(sql, (int(threads_id),))
    thread = cursor.fetchone()
    # print(comments)
    sql = "select tags.id,tags.name from tags_has_threads join tags on tags.id= tags_id where threads_id=%s"
    cursor.execute(sql, (threads_id, ))
    tags = cursor.fetchall()
    return render_template('thread.html', comments=comments, thread=thread, tags=tags)


@app.route('/threads/')
def list_threads():
    sql = """SELECT threads.id, title, content, users_id, concat(users.fname,' ',users.lname) username \
        from threads \
        join users on `users`.`id`= `threads`.`users_id` \
        where blocked = 0 and groups_id is NULL"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    threads = cursor.fetchall()
    print(threads)
    return render_template('threads.html', threads=threads)


@app.route('/threads/new', methods=['POST', 'GET'])
def create_thread():
    if not session['logged_in']:
        flash('You need to login to continue')
        return redirect(url_for('login'))
    if request.method == 'POST':

        db = get_db()
        # db.autocommit(False)
        cursor = db.cursor()

        print(request.form)
        tags = request.form['tags'].split('\r\n')
        tags = [x for x in tags if x != ""]
        print(tags)
        l = len(tags)

        # insert tags before use if missing
        temp = "(" + "),(".join(["%s" for i in range(l)]) + ")"
        sql = "INSERT IGNORE into tags (name) VALUES " + temp
        print(sql)
        cursor.execute(sql, tags)
        s = ""
        for i in range(l):
            s += "%s,"
        else:
            s = s[:-1]
        print(s)
        sql = "SELECT id from tags where name in ( {} )".format(s)
        print(sql)
        cursor.execute(sql, tags)
        if cursor.rowcount != l:
            print("tags retrieved: ", cursor.rowcount, l)
            print(cursor.statement)
            raise Exception("All tags not inserted")
        tag_ids = cursor.fetchall()
        print(tag_ids)

        sql = "INSERT into threads (`title`, `content`, `users_id`) VALUES( %s, %s, %s)"

        print(session['user_id'])
        cursor.execute(sql, (
            request.form['title'],
            request.form['content'],
            int(session['user_id'])
            )
        )
        thread_id = cursor.lastrowid
        sql = "INSERT INTO tags_has_threads (`tags_id`,`threads_id`) VALUES(%s, {})".format(thread_id)
        print(sql, str(tag_ids))
        cursor.executemany(sql, [[i['id']] for i in tag_ids])
        flash("New Thread created", 'success')
        # provide better control here
        return redirect(url_for('show_thread', threads_id=thread_id))

    return render_template('thread_new.html')
