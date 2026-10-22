from pathlib import Path
import pytest
from project.app import create_app, db
from project.models import Post


@pytest.fixture
def client(tmp_path):
    test_app = create_app(dict(TESTING=True, SECRET_KEY='test-only', USERNAME='admin', PASSWORD='admin', SQLALCHEMY_DATABASE_URI='sqlite:///' + str(tmp_path / 'test.db')))
    with test_app.app_context():
        db.create_all()
        yield test_app.test_client()
        db.session.remove()
        db.drop_all()


def login(client, username='admin', password='admin'):
    return client.post('/login', data=dict(username=username, password=password), follow_redirects=True)


def test_index(client):
    assert client.get('/').status_code == 200


def test_database(client):
    assert Path(db.engine.url.database).is_file()
    assert db.session.query(Post).count() == 0


def test_empty_db(client):
    assert b'No entries yet. Add some!' in client.get('/').data


def test_login_logout(client):
    assert b'You were logged in' in login(client).data
    assert b'You were logged out' in client.get('/logout', follow_redirects=True).data
    assert b'Invalid username' in login(client, username='wrong').data
    assert b'Invalid password' in login(client, password='wrong').data


def test_messages(client):
    login(client)
    response = client.post('/add', data=dict(title='<Hello>', text='<strong>HTML</strong> allowed here'), follow_redirects=True)
    assert b'&lt;Hello&gt;' in response.data
    assert b'<strong>HTML</strong> allowed here' in response.data
    assert b'No entries yet. Add some!' not in response.data


def test_delete_message(client):
    login(client)
    client.post('/add', data=dict(title='Delete me', text='temporary'))
    response = client.get('/delete/1')
    assert response.status_code == 200
    assert response.get_json()['status'] == 1
    assert b'Delete me' not in client.get('/').data
