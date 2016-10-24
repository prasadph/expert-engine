import MySQLdb
from flask import Flask, g, session, redirect, url_for, flash
from functools import wraps

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
    db.cursorclass = MySQLdb.cursors.DictCursor
    return db


def get_db():
    if not hasattr('g', 'mysql_db'):
        g.mysql_db = connect_db()
    return g.mysql_db


def login_required(f):
    """Checks whether user is logged in or redirects to login page"""
    @wraps(f)
    def decorator(*args, **kwargs):
        print("works")
        if not session.get('logged_in', 0):
            flash('You need to login to continue')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorator


from views import groups, threads, users


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
