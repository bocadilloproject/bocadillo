from bocadillo import create_client, settings


def test_todos():
    settings._clear()
    from todos.asgi import app

    client = create_client(app)

    r = client.post("/todos", json={"title": "Make breakfast"})
    assert r.status_code == 201
    assert r.json() == {"title": "Make breakfast", "done": False}

    r = client.post(
        "/todos",
        json={"title": "Buy cornflakes at the store and make breakfast"},
    )
    assert r.status_code == 400
    assert "title" in r.json()["detail"]
