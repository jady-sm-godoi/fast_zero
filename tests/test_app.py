from http import HTTPStatus


def test_create_user(client):
    user = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret",
    }
    response = client.post("/users/", json=user)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "alice",
        "email": "alice@example.com",
        "id": 1,
    }


def test_create_user_with_invalid_email(client):
    user = {
        "username": "alice",
        "email": "aliceexamplecom",
        "password": "secret",
    }
    response = client.post("/users/", json=user)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "value is not a valid email address" in response.text


def test_read_users(client):
    user = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret",
    }
    client.post("/users/", json=user)

    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {
                "username": "alice",
                "email": "alice@example.com",
                "id": 1,
            }
        ]
    }


def test_update_user(client):
    user = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret",
    }
    client.post("/users/", json=user)

    user_to_update = {
        "username": "alice no pais das maravilhas",
        "email": "alice@example.com",
        "password": "outropassword",
    }
    response = client.put("/users/1", json=user_to_update)

    assert response.status_code == HTTPStatus.OK
    assert "alice no pais das maravilhas" in response.text


def test_delete_user(client):
    user = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret",
    }
    client.post("/users/", json=user)

    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted successfully"}
