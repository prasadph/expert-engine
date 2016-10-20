from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import MySQLdb
# import flask_mysql

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    # USERNAME='admin',
    # PASSWORD='default',
    DEBUG=True,
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    db = MySQLdb.connect("localhost","forum","forumforum","discussionforum")
    db.autocommit(True)
    db.cursorclass=MySQLdb.cursors.DictCursor
    return db

def get_db():
    if not hasattr('g','mysql_db'):
        g.mysql_db = connect_db()
    return g.mysql_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()

@app.route('/join', methods=['GET','POST'])
def signup():
    error = None
    if request.method == 'POST':
        # print(request.form)
        form = request.form

        db = get_db()
        sql = """INSERT INTO `users` ( `email`, `fname`, `lname`, `password`)
                VALUES (%s, %s, %s, %s)"""
        cursor = db.cursor()
        cursor.execute(sql,(form['email'],form['fname'],form['lname'],form['password']))

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
            cursor.execute(sql,(session['user_id'], ))
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

@app.route('/threads')
def threads():
    sql = "SELECT threads.id, title, content, users_id, concat(users.fname,' ',users.lname) username from threads join users on `users`.`id`= `threads`.`users_id` where blocked = 0 and groups_id is NULL"
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    threads = cursor.fetchall()
    print(threads)
    return render_template('threads.html', threads=threads)

@app.route('/thread/<int:threads_id>')
def thread(threads_id):

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
    return render_template('thread.html', comments=comments, thread=thread)


@app.route('/create',methods=['POST', 'GET'])
def create_thread():
    if not session['logged_in']:
        flash('You need to login to continue')
        return redirect(url_for('login'))
    if request.method == 'POST':

        sql = "INSERT into threads (`title`, `content`, `users_id`) VALUES( %s, %s, %s)"
        db = get_db()
        cursor = db.cursor()
        print(session['user_id'])
        cursor.execute(sql, (
            request.form['title'],
            request.form['content'],
            int(session['user_id'])
            )
        )
    return render_template('thread_new.html')

# @app.route('/')
# @app.route('/hello/<name>')
# def hello_world(name=None):
#     db = get_db()
#     cursor = db.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * from tags")
#     print(cursor.fetchall())
#     # db.commit()
#     return render_template('hello.html', name=name)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
