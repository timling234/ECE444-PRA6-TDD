from pathlib import Path
import pytest
from project.app import app, init_db


@pytest.fixture
def client(tmp_path):
    app.config.update(TESTING=True, DATABASE=str(tmp_path / 'test.db'))
    init_db()
    yield app.test_client()


def login(client, username='admin', password='admin'):
    return client.post('/login', data=dict(username=username, password=password), follow_redirects=True)


def test_index(client):
    assert client.get('/').status_code == 200


def test_database(client):
    assert Path(app.config['DATABASE']).is_file()


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
