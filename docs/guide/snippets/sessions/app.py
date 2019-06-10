# todos/app.py
from bocadillo import App, configure
from . import settings

app = App()
configure(app, settings)


TODOS = [
    {"id": 0, "content": "Go shopping"},
    {"id": 1, "content": "Cook fries"},
    {"id": 2, "content": "Do laundry"},
]


@app.route("/unseen-todos")
async def get_unseen_todos(req, res):
    last_id = req.session.get("last_id", -1)
    unseen_todos = TODOS[last_id + 1 :]

    if unseen_todos:
        req.session["last_id"] = unseen_todos[-1]["id"]

    res.json = unseen_todos


@app.route("/todos", methods=["post"])
async def create_todo(req, res):
    json = await req.json()
    todo = {"id": len(TODOS) + 1, "content": json["content"]}
    TODOS.append(todo)
    res.status_code = 201
