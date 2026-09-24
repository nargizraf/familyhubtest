from datetime import date
from decimal import Decimal

from app.config import settings
from app.seed import seed_demo
from tests.helpers import auth_header, category_id


def _spend(client, headers, amount: str) -> None:
    response = client.post(
        "/api/expenses",
        headers=headers,
        json={
            "amount": amount,
            "description": "Groceries",
            "category_id": category_id(client, headers, "Food"),
            "date": date.today().isoformat(),
        },
    )
    assert response.status_code == 201, response.text


def test_budget_starts_empty_then_warns_when_exceeded(client):
    headers = auth_header(client)
    initial = client.get("/api/budget", headers=headers)
    assert initial.status_code == 200
    assert initial.json()["amount"] is None
    assert initial.json()["over_budget"] is False
    assert Decimal(initial.json()["spent"]) == Decimal("0.00")

    saved = client.put("/api/budget", headers=headers, json={"amount": "50", "currency": "pln"})
    assert saved.status_code == 200, saved.text
    assert Decimal(saved.json()["amount"]) == Decimal("50.00")
    assert saved.json()["currency"] == "PLN"
    assert saved.json()["over_budget"] is False

    _spend(client, headers, "80.00")
    status = client.get("/api/budget", headers=headers).json()
    assert Decimal(status["spent"]) == Decimal("80.00")
    assert Decimal(status["remaining"]) == Decimal("-30.00")
    assert status["over_budget"] is True


def test_dashboard_and_seed_data(client, db):
    assert seed_demo(db) is True
    assert seed_demo(db) is False

    login = client.post(
        "/api/auth/login",
        json={"email": settings.demo_user_email, "password": settings.demo_user_password},
    )
    assert login.status_code == 200, login.text
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    dashboard = client.get("/api/dashboard", headers=headers)
    assert dashboard.status_code == 200, dashboard.text
    body = dashboard.json()
    assert Decimal(body["current_month_spending"]) == Decimal("333.70")
    assert Decimal(body["previous_month_spending"]) == Decimal("1231.15")
    assert Decimal(body["monthly_budget"]) == Decimal("250.00")
    assert Decimal(body["remaining_budget"]) == Decimal("-83.70")
    assert body["over_budget"] is True
    assert body["expense_count"] == 9
    assert body["currency"] == "PLN"
    assert len(body["recent_expenses"]) == 8
    categories = {item["category"] for item in body["spending_by_category"]}
    assert "Food" in categories
    assert "Rent" not in categories
