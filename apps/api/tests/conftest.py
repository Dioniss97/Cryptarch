"""
Fixtures for API tests. Domain tests require PostgreSQL (e.g. docker compose up).
Set DATABASE_URL or DATABASE_URL_TEST to run domain tests.
"""
import os
import subprocess
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure app root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import DATABASE_URL, DATABASE_URL_TEST
    from domain.models import Base
except ImportError:
    DATABASE_URL = DATABASE_URL_TEST = None

_engine = None
_Session = None


def _get_test_url():
    return os.environ.get("DATABASE_URL_TEST", os.environ.get("DATABASE_URL", "")).strip()


def _can_connect_postgres():
    """Try to connect to Postgres; set global _engine and _Session."""
    global _engine, _Session
    url = _get_test_url()
    if not url or "postgresql" not in url:
        return False
    try:
        _engine = create_engine(url, pool_pre_ping=True)
        conn = _engine.connect()
        conn.close()
        _Session = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
        return True
    except Exception:
        return False


def _run_migrations():
    """Run Alembic migrations to head (subprocess so env.py sees DATABASE_URL)."""
    if not _engine:
        return
    api_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = os.environ.copy()
    env["DATABASE_URL"] = _get_test_url()
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=api_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        pytest.skip(f"Migrations failed: {r.stderr or r.stdout}")


@pytest.fixture(scope="session")
def db_engine():
    """Postgres engine for domain tests; skip if unavailable."""
    if not _can_connect_postgres():
        pytest.skip("PostgreSQL not available (set DATABASE_URL or DATABASE_URL_TEST)")
    _run_migrations()
    return _engine


@pytest.fixture
def db_session(db_engine):
    """Transactional session; rollback after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = _Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
