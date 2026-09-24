def register(
    client,
    email: str = "user@example.com",
    password: str = "Password1",
    full_name: str = "Test User",
) -> dict:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth_header(client, email: str = "user@example.com", password: str = "Password1") -> dict[str, str]:
    body = register(client, email=email, password=password)
    return {"Authorization": f"Bearer {body['access_token']}"}


def category_id(client, headers: dict[str, str], name: str = "Food") -> str:
    response = client.get("/api/categories", headers=headers)
    assert response.status_code == 200, response.text
    return next(item["id"] for item in response.json() if item["name"] == name)
