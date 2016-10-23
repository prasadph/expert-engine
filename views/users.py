from flask import request, session, g, redirect, url_for, abort, \
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
        sql = "SELECT id, email, fname, lname from users where email= %s and password= %s limit 1"
        db = get_db()
        cursor = db.cursor()
        cursor.execute(sql, (request.form['email'], request.form['password']))
        if cursor.rowcount:
            session['logged_in'] = True
            user = cursor.fetchone()
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['fname'] = user['fname']
            session['lname'] = user['lname']
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
