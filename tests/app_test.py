from pathlib import Path
import pytest
from project.app import create_app, db
from project.models import Post


@pytest.fixture
def client(tmp_path):
    test_app = create_app(
        dict(
            TESTING=True,
            SECRET_KEY="test-only",
            USERNAME="admin",
            PASSWORD="admin",
            SQLALCHEMY_DATABASE_URI="sqlite:///" + str(tmp_path / "test.db"),
        )
    )
    with test_app.app_context():
        db.create_all()
        yield test_app.test_client()
        db.session.remove()
        db.drop_all()


def login(client, username="admin", password="admin"):
    return client.post(
        "/login", data=dict(username=username, password=password), follow_redirects=True
    )


def test_index(client):
    assert client.get("/").status_code == 200


def test_database(client):
    assert Path(db.engine.url.database).is_file()
    assert db.session.query(Post).count() == 0


def test_empty_db(client):
    assert b"No entries yet. Add some!" in client.get("/").data


def test_login_logout(client):
    assert b"You were logged in" in login(client).data
    assert b"You were logged out" in client.get("/logout", follow_redirects=True).data
    assert b"Invalid username" in login(client, username="wrong").data
    assert b"Invalid password" in login(client, password="wrong").data


def test_messages(client):
    login(client)
    response = client.post(
        "/add",
        data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
        follow_redirects=True,
    )
    assert b"&lt;Hello&gt;" in response.data
    assert b"<strong>HTML</strong> allowed here" in response.data
    assert b"No entries yet. Add some!" not in response.data


def test_delete_message(client):
    login(client)
    client.post("/add", data=dict(title="Delete me", text="temporary"))
    response = client.get("/delete/1")
    assert response.status_code == 200
    assert response.get_json()["status"] == 1
    assert b"Delete me" not in client.get("/").data


@pytest.mark.parametrize(
    "query,expected,absent",
    [
        ("ALPHA", "Alpha title", "Other title"),
        ("needle", "Other title", "Alpha title"),
        ("missing", None, "Alpha title"),
    ],
)
def test_search_title_body_case_insensitive(client, query, expected, absent):
    db.session.add_all(
        [
            Post(title="Alpha title", text="first body"),
            Post(title="Other title", text="a NEEDLE here"),
        ]
    )
    db.session.commit()
    response = client.get("/search/", query_string={"query": query})
    assert response.status_code == 200
    if expected:
        assert expected.encode() in response.data
    assert absent.encode() not in response.data


def test_search_without_query(client):
    response = client.get("/search/")
    assert response.status_code == 200
    assert b"Search" in response.data


def test_search_results_use_real_post_id(client):
    db.session.add(Post(id=42, title="Find this", text="body"))
    db.session.commit()
    assert b'id="42"' in client.get("/search/?query=Find").data


def test_anonymous_delete_is_denied_and_preserves_post(client):
    db.session.add(Post(title="Keep this", text="Protected"))
    db.session.commit()
    response = client.get("/delete/1")
    assert response.status_code == 401
    assert response.get_json() == {"status": 0, "message": "Please log in."}
    assert db.session.get(Post, 1) is not None


def test_logout_revokes_delete_permission(client):
    login(client)
    client.post("/add", data=dict(title="Keep after logout", text="Protected"))
    client.get("/logout")
    assert client.get("/delete/1").status_code == 401
    assert db.session.get(Post, 1) is not None


def test_anonymous_add_is_denied(client):
    assert (
        client.post("/add", data=dict(title="Forbidden", text="Denied")).status_code
        == 401
    )
    assert db.session.query(Post).count() == 0


def test_body_keeps_formatting_but_removes_active_html(client):
    login(client)
    response = client.post(
        "/add",
        data=dict(
            title="Safe body", text="<strong>bold</strong><script>alert(1)</script>"
        ),
        follow_redirects=True,
    )
    assert b"<strong>bold</strong>" in response.data
    assert b"<script>alert(1)</script>" not in response.data


def test_postgres_url_uses_installed_psycopg2_driver(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://demo:demo@localhost/flaskr')
    postgres_app = create_app({'TESTING': True})
    with postgres_app.app_context():
        assert db.engine.url.drivername == 'postgresql+psycopg2'


def test_legacy_postgres_url_is_normalized(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgres://demo:demo@localhost/flaskr')
    postgres_app = create_app({'TESTING': True})
    with postgres_app.app_context():
        assert db.engine.url.drivername == 'postgresql+psycopg2'
