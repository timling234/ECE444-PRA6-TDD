import os
import secrets
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, session, flash, redirect, url_for, abort, jsonify

from project.models import db, Post


def create_app(test_config=None):
    app = Flask(__name__)
    url = os.getenv('DATABASE_URL', 'sqlite:///' + str(Path(__file__).resolve().parent / 'flaskr.db'))
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        USERNAME=os.getenv('ADMIN_USERNAME', 'admin'),
        PASSWORD=os.getenv('ADMIN_PASSWORD', 'admin'),
        SECRET_KEY=os.getenv('SECRET_KEY') or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    register_routes(app)
    return app


def login_required(view):
    @wraps(view)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in.')
            return jsonify(status=0, message='Please log in.'), 401
        return view(*args, **kwargs)
    return decorated_function


def register_routes(app):
    @app.route('/')
    def index():
        entries = db.session.query(Post).order_by(Post.id.desc()).all()
        return render_template('index.html', entries=entries)


    @app.route('/search/')
    def search():
        query = request.args.get('query', '')
        entries = db.session.query(Post).order_by(Post.id.desc()).all() if query else []
        entries = [entry for entry in entries if query.lower() in entry.title.lower() or query.lower() in entry.text.lower()]
        return render_template('search.html', entries=entries, query=query)


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if request.form.get('username') != app.config['USERNAME']:
                error = 'Invalid username'
            elif request.form.get('password') != app.config['PASSWORD']:
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                flash('You were logged in')
                return redirect(url_for('index'))
        return render_template('login.html', error=error)


    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        flash('You were logged out')
        return redirect(url_for('index'))


    @app.route('/add', methods=['POST'])
    def add_entry():
        if not session.get('logged_in'):
            abort(401)
        db.session.add(Post(title=request.form['title'], text=request.form['text']))
        db.session.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('index'))


    @app.route('/delete/<int:post_id>')
    @login_required
    def delete_entry(post_id):
        db.session.query(Post).filter_by(id=post_id).delete()
        db.session.commit()
        flash('The entry was deleted.')
        return jsonify(status=1, message='Post Deleted')


app = create_app()
