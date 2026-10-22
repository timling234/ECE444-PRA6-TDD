import sqlite3
from flask import Flask, g, render_template, request, session, flash, redirect, url_for, abort

app = Flask(__name__)
app.config['DATABASE'] = 'flaskr.db'


def get_db():
    if 'sqlite_db' not in g:
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


def init_db():
    with app.app_context():
        database = get_db()
        with app.open_resource('schema.sql', mode='r') as schema:
            database.executescript(schema.read())
        database.commit()


@app.teardown_appcontext
def close_db(error):
    database = g.pop('sqlite_db', None)
    if database is not None:
        database.close()


app.config.update(USERNAME='admin', PASSWORD='admin', SECRET_KEY='local-development-only')


@app.route('/')
def index():
    entries = get_db().execute('select * from entries order by id desc').fetchall()
    return render_template('index.html', entries=entries)


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
    database = get_db()
    database.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
    database.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))
