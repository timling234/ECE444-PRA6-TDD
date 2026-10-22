"""Start the local demo with one command: python run_app.py."""

import argparse
import hashlib
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import venv
import webbrowser

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--managed-runtime", action="store_true", help=argparse.SUPPRESS
    )
    args = parser.parse_args()
    os.chdir(ROOT)

    if not args.managed_runtime:
        environment = ROOT / ".venv"
        python = environment / (
            "Scripts/python.exe" if os.name == "nt" else "bin/python"
        )
        if not python.exists():
            print("Preparing the local Python environment...", flush=True)
            venv.EnvBuilder(with_pip=True).create(environment)
        requirements = ROOT / "requirements.txt"
        fingerprint = hashlib.sha256(requirements.read_bytes()).hexdigest()
        marker = environment / ".pra6-requirements.sha256"
        if not marker.exists() or marker.read_text().strip() != fingerprint:
            print("Installing project dependencies (first run only)...", flush=True)
            subprocess.check_call(
                [str(python), "-m", "pip", "install", "-r", str(requirements)]
            )
            marker.write_text(fingerprint)
        command = [
            str(python),
            str(ROOT / "run_app.py"),
            "--managed-runtime",
            "--port",
            str(args.port),
        ]
        if args.no_browser:
            command.append("--no-browser")
        try:
            return subprocess.call(command)
        except KeyboardInterrupt:
            return 0

    from project.app import create_app, db

    instance = ROOT / "instance"
    instance.mkdir(exist_ok=True)
    secret_file = instance / ".secret-key"
    if not secret_file.exists():
        secret_file.write_text(secrets.token_hex(32))
    app = create_app(
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(instance / "flaskr.db"),
            "SECRET_KEY": secret_file.read_text().strip(),
        }
    )
    with app.app_context():
        db.create_all()
    address = f"http://127.0.0.1:{args.port}/"
    print(
        f"\nFlaskr: {address}\nLogin: admin / admin (unless overridden by ADMIN_USERNAME/ADMIN_PASSWORD)\nKeep this terminal open. Press Ctrl+C to stop.\n",
        flush=True,
    )
    if not args.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(address)).start()
    app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
