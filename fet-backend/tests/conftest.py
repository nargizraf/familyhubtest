import os
import re
import subprocess
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.database import get_db
from app.main import app

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _ensure_test_database() -> None:
    database_name = settings.test_database_url.rsplit("/", 1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9_]+", database_name):
        raise RuntimeError(f"Refusing to create database named {database_name!r}")
    admin_url = settings.test_database_url.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": database_name},
        ).scalar()
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    admin_engine.dispose()


def _migrate() -> None:
    env = os.environ.copy()
    env["DATABASE_URL"] = settings.test_database_url
    subprocess.run(["alembic", "upgrade", "head"], cwd=BACKEND_ROOT, env=env, check=True)


@pytest.fixture(scope="session")
def engine():
    _ensure_test_database()
    _migrate()
    test_engine = create_engine(settings.test_database_url, pool_pre_ping=True)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def db(engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE expenses, budgets, categories, users RESTART IDENTITY CASCADE"))


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
