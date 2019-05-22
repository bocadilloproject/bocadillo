import os

import pytest

from bocadillo import create_client, settings


@pytest.fixture(autouse=True, scope="module")
def setup_env():
    os.environ["SECRET_KEY"] = "1234"
    yield
    os.environ.pop("SECRET_KEY")


def test_todos():
    settings._clear()
    from .app import app

    client = create_client(app)

    r = client.get("/unseen-todos")
    assert r.status_code == 200
    assert len(r.json()) == 3

    r = client.get("/unseen-todos")
    assert r.status_code == 200
    assert len(r.json()) == 0

    r = client.post("/todos", json={"content": "test"})
    assert r.status_code == 201

    r = client.get("/unseen-todos")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["content"] == "test"
