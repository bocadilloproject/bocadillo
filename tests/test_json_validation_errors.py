import pytest
import typesystem

from bocadillo import configure, create_client


class Todo(typesystem.Schema):
    title = typesystem.String(max_length=50)
    done = typesystem.Boolean(default=False)


def test_handle_validation_errors(app, client):
    @app.route("/todos")
    class TodoList:
        async def post(self, req, res):
            todo = Todo.validate(await req.json())
            res.json = dict(todo)

    r = client.post("/todos", json={"title": "Make sugar"})
    assert r.status_code == 200
    assert r.json() == {"title": "Make sugar", "done": False}

    r = client.post("/todos", json={"title": "Very long string" * 10})
    assert r.status_code == 400
    assert r.json()["detail"] == {
        "title": "Must have no more than 50 characters."
    }


def test_disable_validation_error_handling(raw_app):
    app = configure(raw_app, handle_typesystem_validation_errors=False)
    client = create_client(app)

    @app.route("/todos")
    class TodoList:
        async def post(self, req, res):
            todo = Todo.validate(await req.json())
            res.json = dict(todo)

    with pytest.raises(typesystem.ValidationError):
        client.post("/todos", json={"title": "Very long string" * 10})
