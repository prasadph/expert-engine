from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash
from app import app, get_db


@app.route('/groups/search')
def group_search():
    """Lets you search groups across the site"""
    return render_template("groups/search.html")


# needs to be protected
@app.route('/groups/list')
def group_list():
    """Lets you views your groups"""
    db = get_db()
    cursor = db.cursor()
    sql = """SELECT * from groups \
    join users_has_groups on groups.id=users_has_groups.groups_id  \
    where users_id=%s"""
    cursor.execute(sql, (session['user_id'],))
    groups = cursor.fetchall()
    return render_template("groups/list.html", groups=groups)


# needs to be protected
@app.route('/groups/view/<int:groups_id>')
def group_view(groups_id):
    """Lets you view a group"""
    db = get_db()
    cursor = db.cursor()
    sql = """SELECT * from groups where id=%s"""
    cursor.execute(sql, (groups_id, ))
    group = cursor.fetchone()
    # need to display group members
    # consider using same template as thread view
    return render_template("groups/view.html", group=group)


@app.route('/groups/new', methods=['GET', 'POST'])
def group_create():
    """Lets you create new groups"""
    if not session['logged_in']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db()
        db.autocommit(False)
        group_name = request.form['name']
        emails = request.form['emails'].split('\r\n')
        print(emails)
        try:
            cursor = db.cursor()

            sql = """INSERT into groups (`name`, `admin`) VALUES(%s, %s)"""
            cursor.execute(sql, (group_name, session['user_id']))
            group_id = cursor.lastrowid

            l = len(emails)
            s = ""
            for i in range(l):
                s += "%s,"
            else:
                s = s[:-1]
            sql = """SELECT id from users where email in ({})""".format(s)
            # print(sql)
            cursor.execute(sql, emails)
            user_ids = cursor.fetchall()
            user_ids = [(i['id'],) for i in user_ids]
            user_ids.append((session['user_id'],))
            #user_ids = list(user_ids).append({'id': int(session['user_id'])})
            sql = """INSERT into users_has_groups (`users_id`,`groups_id`) VALUES (%s, {})""".format(group_id)
            print("user_id", user_ids, sql)
            cursor.executemany(sql, user_ids)
            print(cursor.lastrowid)
            db.commit()
            flash("Created new group")
        except Exception as e:
            db.rollback()
            print(e)
            abort(401)
        return redirect(url_for('group_view', groups_id=group_id))
        # abort(401)
    return render_template("groups/create.html")