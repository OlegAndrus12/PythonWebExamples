"""CRUD over HTTP: read the board, add a service, remove it."""

import services


def test_read(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Example" in response.data


def test_create(client):
    response = client.post("/services", data={"name": "New", "url": "new.example"})

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert services.load()["New"] == "https://new.example"


def test_create_ignores_blank_input(client):
    before = services.load()

    client.post("/services", data={"name": "", "url": ""})

    assert services.load() == before


def test_create_ignores_duplicate_name(client):
    before = services.load()

    client.post("/services", data={"name": "Example", "url": "other.example"})

    assert services.load() == before


def test_delete(client):
    response = client.post("/services/delete", data={"name": "Example"})

    assert response.status_code == 302
    assert "Example" not in services.load()
