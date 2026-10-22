"""Run the PRA6 tests with: python test.py (optional pytest arguments follow)."""

import os
from pathlib import Path
import subprocess
import sys
import venv


def main():
    root = Path(__file__).resolve().parent
    environment = root / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        print("Preparing the test environment...", flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)
    available = subprocess.run(
        [str(python), "-c", "import pytest, flask, flask_sqlalchemy, bleach, psycopg2"],
        capture_output=True,
        cwd=root,
    )
    if available.returncode:
        subprocess.check_call(
            [str(python), "-m", "pip", "install", "-r", str(root / "requirements.txt")],
            cwd=root,
        )
    return subprocess.call([str(python), "-m", "pytest", *sys.argv[1:]], cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
