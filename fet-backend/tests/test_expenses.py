from datetime import date
from decimal import Decimal

from tests.helpers import auth_header, category_id


def test_expense_crud_filter_and_sort(client):
    headers = auth_header(client)
    food = category_id(client, headers, "Food")
    travel = category_id(client, headers, "Travel")
    today = date.today().isoformat()

    created = client.post(
        "/api/expenses",
        headers=headers,
        json={
            "amount": "12.5",
            "description": "  Morning coffee  ",
            "category_id": food,
            "date": today,
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert Decimal(body["amount"]) == Decimal("12.50")
    assert body["currency"] == "PLN"
    assert body["description"] == "Morning coffee"
    assert body["category"] == "Food"
    expense_id = body["id"]

    other = client.post(
        "/api/expenses",
        headers=headers,
        json={
            "amount": "80",
            "currency": "eur",
            "description": "Train ticket",
            "category_id": travel,
            "date": "2024-01-15",
        },
    )
    assert other.status_code == 201, other.text

    listed = client.get("/api/expenses", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 2

    filtered = client.get("/api/expenses", headers=headers, params={"category_id": food, "q": "coffee"})
    assert [item["id"] for item in filtered.json()] == [expense_id]

    by_date = client.get(
        "/api/expenses",
        headers=headers,
        params={"date_from": "2024-01-01", "date_to": "2024-01-31"},
    )
    assert [item["description"] for item in by_date.json()] == ["Train ticket"]

    by_amount = client.get("/api/expenses", headers=headers, params={"sort": "amount", "order": "asc"})
    amounts = [Decimal(item["amount"]) for item in by_amount.json()]
    assert amounts == sorted(amounts)

    by_category = client.get("/api/expenses", headers=headers, params={"sort": "category", "order": "asc"})
    assert [item["category"] for item in by_category.json()] == ["Food", "Travel"]

    fetched = client.get(f"/api/expenses/{expense_id}", headers=headers)
    assert fetched.status_code == 200

    updated = client.put(
        f"/api/expenses/{expense_id}",
        headers=headers,
        json={
            "amount": "15.00",
            "currency": "USD",
            "description": "Latte",
            "category_id": food,
            "date": today,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "Latte"
    assert updated.json()["currency"] == "USD"

    deleted = client.delete(f"/api/expenses/{expense_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/expenses/{expense_id}", headers=headers).status_code == 404


def test_users_cannot_see_each_others_expenses(client):
    first = auth_header(client, email="one@example.com")
    second = auth_header(client, email="two@example.com")
    food = category_id(client, first, "Food")
    created = client.post(
        "/api/expenses",
        headers=first,
        json={
            "amount": "9.00",
            "description": "Secret snack",
            "category_id": food,
            "date": date.today().isoformat(),
        },
    )
    expense_id = created.json()["id"]
    assert client.get("/api/expenses", headers=second).json() == []
    assert client.get(f"/api/expenses/{expense_id}", headers=second).status_code == 404
    assert (
        client.put(
            f"/api/expenses/{expense_id}",
            headers=second,
            json={
                "amount": "1.00",
                "description": "Nope",
                "category_id": category_id(client, second, "Food"),
                "date": date.today().isoformat(),
            },
        ).status_code
        == 404
    )
    assert client.delete(f"/api/expenses/{expense_id}", headers=second).status_code == 404


def test_expense_requires_owned_category(client):
    owner = auth_header(client, email="owner@example.com")
    other = auth_header(client, email="other@example.com")
    foreign_category = category_id(client, other, "Rent")
    response = client.post(
        "/api/expenses",
        headers=owner,
        json={
            "amount": "10.00",
            "description": "Rent",
            "category_id": foreign_category,
            "date": date.today().isoformat(),
        },
    )
    assert response.status_code == 404
