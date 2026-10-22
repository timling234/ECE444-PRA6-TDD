# TA demo guide

## 4-minute demonstration

1. Open the live URL (once verified). Explain Flask handles requests, Jinja renders HTML, SQLAlchemy talks to Postgres, Gunicorn serves the Flask app on Render.
2. Show the test command and 15 passing tests. Explain a red/green record in evidence/; show Git history rather than claiming code was written test-first without evidence.
3. Log in with demo credentials; show invalid credentials produce errors. Session stores logged_in in a signed cookie, and SECRET_KEY must stay stable across production workers.
4. Add two disposable posts. Search by title and by a mixed-case word in the body. Click one post to delete; confirm it disappears, refresh and verify it stays deleted. The JavaScript fetch reads the post's h2 ID and consumes JSON status.
5. Log out and attempt deletion; expect HTTP 401, status 0 and Please log in. Verify the post remains. Explain the decorator uses wraps to preserve Flask's endpoint metadata.
6. Refresh from another browser/session to demonstrate the same persisted PostgreSQL data. Show Render successful deployment and service environment key names without revealing values.

## Explain the suite

- test_index: home route responds HTTP 200.
- test_database: isolated SQLite file exists and Post table is initially empty.
- test_empty_db: empty-state message renders.
- test_login_logout: valid credentials and both invalid credential branches; logout confirmation.
- test_messages: authenticated posting, escaped title and permitted HTML body formatting.
- test_delete_message: authenticated deletion returns success and the actual post disappears from the database-backed home page.
- test_search_title_body_case_insensitive (3 cases): title match, body match and nonmatch, mixed-case input.
- test_search_without_query: search page handles absent input.
- test_search_results_use_real_post_id: rendered deletion target uses actual primary key 42.
- test_anonymous_delete_is_denied_and_preserves_post: HTTP and JSON contract, plus database preservation.
- test_logout_revokes_delete_permission: permission does not persist after logout.
- test_anonymous_add_is_denied: unauthenticated POST cannot create a row.
- test_body_keeps_formatting_but_removes_active_html: preserves strong tags while stripping script markup.

## Concepts to rehearse

Red: run a new test and observe failure because behavior is missing. Green: implement enough to pass. Refactor: improve structure while rerunning tests. Tests here exercise Flask routes and a real isolated database, so many are integration tests rather than pure unit tests.

Fixture: factory creates a new app with TESTING enabled and a new temporary SQLite DB before extension initialization. create_all sets up; session.remove and drop_all tear down. Production DATABASE_URL cannot redirect these tests to production because the fixture overrides the URI.

GET reads pages; POST sends login/post data; redirects implement post-redirect-get. Tutorial deletion uses GET; a production app should use a state-changing method and CSRF protection. JSON is consumed by browser fetch, whereas Jinja renders HTML server-side.

SQLite is a local file; PostgreSQL is a remote server and persists independently from the web instance's ephemeral filesystem. Internal URL is for Render service connections; External URL is for local access and must remain secret. create_all creates missing tables but is not a schema migration tool.

Never tell the TA deployment or submission is complete until the actual public URL, database behavior and submission confirmation are verified.
