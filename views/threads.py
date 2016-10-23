from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash
from app import app, get_db


@app.route('/threads/<int:threads_id>', methods=['GET', 'POST'])
def show_thread(threads_id):

    db = get_db()
    cursor = db.cursor()

    sql = """SELECT threads.id, content, title, threads.created, \
    concat(users.fname,' ',users.lname) username \
    from threads \
    join users on users.id= threads.users_id \
    where threads.id= %s and groups_id is null \
    limit 1"""
    # checking for groups_id allows us to block private threads
    cursor.execute(sql, (int(threads_id),))
    thread = cursor.fetchone()

    if request.method == 'POST':
        user_id = session['user_id']
        comment_text = request.form['text']
        sql = """INSERT into comments (`text`, `threads_id`, `users_id`) VALUES (%s, %s, %s)"""
        cursor.execute(sql, (comment_text, threads_id, user_id))
        flash("New Reply Added")

    sql = """SELECT comments.id, comments.text, concat(users.fname,' ',users.lname) username, comments.created \
    from comments \
    join users on comments.users_id=users.id \
    where threads_id= %s and blocked=0 \
    order by comments.created desc"""
    cursor.execute(sql, (int(threads_id),))
    comments = cursor.fetchall()
    print(comments)

    # print(comments)
    sql = """SELECT tags.id,tags.name \
    from tags_has_threads \
    join tags on tags.id= tags_id \
    where threads_id=%s \
    """
    cursor.execute(sql, (threads_id, ))
    tags = cursor.fetchall()
    return render_template('threads/thread.html', comments=comments, thread=thread, tags=tags)


@app.route('/threads')
def list_threads():
    sql = """SELECT threads.id, title, content, users_id, threads.created, concat(users.fname,' ',users.lname) username \
        from threads \
        join users on `users`.`id`= `threads`.`users_id` \
        where blocked = 0 and groups_id is NULL
        order by threads.created desc limit %s , %s"""
    page = request.args.get('page','1')
    page = int(page)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql, (page * 10, 10))
    threads = cursor.fetchall()
    return render_template('threads/threads.html', threads=threads)


@app.route('/threads/tags/<int:tags_id>')
def threads_by_tagid(tags_id):
    sql = """SELECT threads.id, title, content, users_id, threads.created, concat(users.fname,' ',users.lname) username \
        from threads \
        join users on `users`.`id`= `threads`.`users_id` \
        join tags_has_threads on `tags_has_threads`.`threads_id`= `threads`.`id` \
        where blocked = 0 and groups_id is NULL and tags_id= %s \
        order by threads.created desc"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT tags.name from tags where tags.id= %s limit 1",(tags_id,))
    tag = cursor.fetchone()
    if not tag:
        abort(404)
    cursor.execute(sql, (tags_id,))
    threads = cursor.fetchall()
    return render_template('threads/threads_by_tagid.html', threads=threads, tag=tag)

@app.route('/threads/search')
def threads_search():
    sql = """SELECT distinct threads.id, threads.title, threads.content, threads.created,concat(users.fname,' ',users.lname) username
        from threads
        join users on users.id= threads.users_id
        join tags_has_threads on tags_has_threads.threads_id= threads.id
        join tags on tags_has_threads.tags_id= tags.id
        where threads.title LIKE %s and groups_id is NULL or tags.name LIKE %s
        order by created desc"""
    db = get_db()
    cursor = db.cursor()
    try:
        searchword = request.args.get('keyword')
    except KeyError:
        abort(401)
    if not searchword :
        return redirect(url_for('list_threads'))
    tup = ("%"+searchword+ "%")
    cursor.execute(sql, (tup,tup))
    threads = cursor.fetchall()
    return render_template('threads/search.html', threads=threads, searchword=searchword)

@app.route('/threads/tags')
def display_all_tags():
    sql = """SELECT  tags.id, tags.name, count(*) c\
        from tags \
        join tags_has_threads on `tags_has_threads`.`tags_id`= `tags`.`id` \
        group by tags.id
        order by c desc"""
    # sql query will list tags even if thread are protected
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    tags= cursor.fetchall()
    return render_template('threads/tags.html', tags=tags)

def thread_new(user_id, form, groups_id=None):
    db = get_db()
    db.autocommit(False)
    cursor = db.cursor()
    try:
        tags = form['tags'].split('\r\n')
        tags = [x.lower() for x in tags if x != ""]
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

        cursor.execute(sql, (
            form['title'],
            form['content'],
            user_id
            )
        )
        thread_id = cursor.lastrowid
        sql = "INSERT INTO tags_has_threads (`tags_id`,`threads_id`) VALUES(%s, {})".format(thread_id)
        print(sql, str(tag_ids))
        cursor.executemany(sql, [[i['id']] for i in tag_ids])
        flash("New Thread created", 'success')
        # provide better control here
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
        abort(401)
    return thread_id

@app.route('/threads/new', methods=['POST', 'GET'])
def create_thread():
    if not session['logged_in']:
        flash('You need to login to continue')
        return redirect(url_for('login'))
    if request.method == 'POST':
        form = request.form
        user_id = int(session['user_id'])
        thread_id = thread_new(user_id, form)
        return redirect(url_for('show_thread', threads_id=thread_id))


    return render_template('threads/thread_new.html')
