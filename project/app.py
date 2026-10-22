import sqlite3
from flask import Flask, g

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


@app.route('/')
def hello():
    return 'Hello, World!'
