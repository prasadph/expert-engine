from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash
from app import app, get_db


@app.route('/groups/search')
def group_search():
    """Lets you search groups across the site"""
    return render_template("groups/search.html")


@app.route('/groups/list')
def group_list():
    """Lets you views your groups"""
    return render_template("groups/search.html")


@app.route('/groups/views/<int:groups_id>')
def group_view(groups_id):
    """Lets you view a group"""
    return render_template("groups/search.html")


@app.route('/groups/new')
def group_create():
    """Lets you create new groups"""
    return render_template("groups/search.html")