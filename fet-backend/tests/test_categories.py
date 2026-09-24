from datetime import date

from tests.helpers import auth_header, category_id


def test_category_crud(client):
    headers = auth_header(client)
    created = client.post("/api/categories", headers=headers, json={"name": "  School supplies  "})
    assert created.status_code == 201, created.text
    category = created.json()
    assert category["name"] == "School supplies"

    duplicate = client.post("/api/categories", headers=headers, json={"name": "school supplies"})
    assert duplicate.status_code == 409

    updated = client.put(f"/api/categories/{category['id']}", headers=headers, json={"name": "Education"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Education"

    deleted = client.delete(f"/api/categories/{category['id']}", headers=headers)
    assert deleted.status_code == 204
    names = [item["name"] for item in client.get("/api/categories", headers=headers).json()]
    assert "Education" not in names


def test_cannot_delete_category_in_use(client):
    headers = auth_header(client)
    food = category_id(client, headers, "Food")
    created = client.post(
        "/api/expenses",
        headers=headers,
        json={
            "amount": "5.00",
            "description": "Bread",
            "category_id": food,
            "date": date.today().isoformat(),
        },
    )
    assert created.status_code == 201, created.text
    blocked = client.delete(f"/api/categories/{food}", headers=headers)
    assert blocked.status_code == 409


def test_cannot_edit_another_users_category(client):
    first = auth_header(client, email="cat-one@example.com")
    second = auth_header(client, email="cat-two@example.com")
    food = category_id(client, first, "Food")
    response = client.put(f"/api/categories/{food}", headers=second, json={"name": "Hijacked"})
    assert response.status_code == 404
