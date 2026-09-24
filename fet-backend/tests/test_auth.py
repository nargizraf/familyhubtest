from sqlalchemy import select, text

from app.models import User
from tests.helpers import auth_header, register


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/health").json() == {"status": "ok"}


def test_schema_created_by_migration(db):
    tables = set(
        db.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        ).scalars()
    )
    assert {"users", "categories", "expenses", "budgets"} <= tables
    indexes = set(db.execute(text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")).scalars())
    assert "ix_users_email" in indexes
    assert "ix_expenses_user_date" in indexes
    foreign_keys = db.execute(text("SELECT count(*) FROM pg_constraint WHERE contype = 'f'")).scalar()
    assert foreign_keys >= 4


def test_register_login_and_me(client, db):
    created = register(client, email="Person@Example.com", full_name="  Pat  Example ")
    assert created["user"]["email"] == "person@example.com"
    assert created["user"]["full_name"] == "Pat Example"
    assert created["token_type"] == "bearer"

    user = db.scalar(select(User).where(User.email == "person@example.com"))
    assert user is not None
    assert user.password_hash != "Password1"
    assert user.password_hash.startswith("$2")

    login = client.post("/api/auth/login", json={"email": "person@example.com", "password": "Password1"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "person@example.com"

    rejected = client.post("/api/auth/login", json={"email": "person@example.com", "password": "wrong-password"})
    assert rejected.status_code == 401

    missing = client.get("/api/auth/me")
    assert missing.status_code == 401

    invalid = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert invalid.status_code == 401


def test_duplicate_email(client):
    register(client)
    again = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "Password1", "full_name": "Other"},
    )
    assert again.status_code == 409


def test_register_creates_default_categories(client):
    headers = auth_header(client)
    response = client.get("/api/categories", headers=headers)
    names = sorted(item["name"] for item in response.json())
    assert names == [
        "Entertainment",
        "Food",
        "Other",
        "Rent",
        "Shopping",
        "Transport",
        "Travel",
        "Utilities",
    ]


def test_expenses_require_auth(client):
    assert client.get("/api/expenses").status_code == 401
    assert client.get("/api/categories").status_code == 401
    assert client.get("/api/budget").status_code == 401
    assert client.get("/api/dashboard").status_code == 401
