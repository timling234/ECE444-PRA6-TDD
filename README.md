# ECE444 PRA6 - Flaskr TDD and Deployment

Personal repository: https://github.com/timling234/ECE444-PRA6-TDD
Course instructions: https://github.com/shuruizUofT/flaskr-tdd/blob/main/README.md

## Run locally (PowerShell)

Open this folder in VS Code, open its terminal, and run:

```powershell
python run_app.py
```

The launcher creates a virtual environment, installs pinned requirements on first run, creates a local SQLite database, starts Flask at http://127.0.0.1:5001/ and opens the browser. Keep the terminal open; Ctrl+C stops it. Later runs reuse the environment and data. If port 5001 is already used, run `python run_app.py --port 5002`.

The tutorial demo credentials are admin / admin. Use only disposable demo content. Set ADMIN_USERNAME and ADMIN_PASSWORD to override them. The launcher saves a local session key inside the ignored instance/ folder. Render uses its own SECRET_KEY and PostgreSQL DATABASE_URL. Never commit .env or database credentials.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m flake8 project tests create_db.py
.\.venv\Scripts\python.exe -m black --workers 1 --check project tests create_db.py
```

Verified locally: 15 tests passed; Flake8 and Black checks exited 0. Logs are in evidence/. First Hello World, SQLite, blog, deletion, search, authorization and HTML sanitization stages have actual test execution records. 06-blog-environment-error.txt is an environment failure, not a successful run; the subsequent six-test SQLite run and ORM runs passed.

The factory configures each test database before SQLAlchemy initialization so tests never touch the deployment database. Each test gets a temporary SQLite database and drops its tables afterward.

## Deploy to Render

Use a free Python Web Service and a free PostgreSQL instance in the same region. Free Postgres currently expires after 30 days (the live dashboard differs from the course README's 90-day statement).

- Repository: this repository, branch main
- Build: `pip install -r requirements.txt`
- Start: `python create_db.py && gunicorn project.app:app --bind 0.0.0.0:$PORT`
- PYTHON_VERSION: 3.12.14 (matches verified local interpreter)
- DATABASE_URL: PostgreSQL Internal Database URL, supplied only through Render environment settings
- SECRET_KEY: generated stable random secret
- Health check: `/`

render.yaml also describes these resources. create_db.py only creates missing tables, and does not erase posts. DATABASE_URL supports postgres:// normalization; without it the app uses local SQLite. The server binds to Render's PORT. Gunicorn runs on the Linux deployment platform; local Windows uses Flask's development server.

## Tutorial adaptations

Uses an app factory and separate extension/model module to avoid circular imports and ensure isolated database fixtures with current Flask-SQLAlchemy. Bootstrap shares a base template. Search results use the actual entry.id (fixing the tutorial's entry.post_id typo). HTML body formatting is preserved for allowed tags and sanitized with Bleach before rendering. GET deletion is retained to match the course tutorial; this is a course demonstration, not a production authentication system.

## Submission and demo status

Quercus submission link: https://q.utoronto.ca/courses/468834/assignments/1848474
Submit the GitHub repository URL in its text box. The page shows Nov 6, 2026 at 11:59 p.m.; it also says grading must occur in person before the end of your enrolled PRA session.

Deployment, live PostgreSQL verification and Quercus submission are still pending. See TASKS.md and TA_DEMO.md.
