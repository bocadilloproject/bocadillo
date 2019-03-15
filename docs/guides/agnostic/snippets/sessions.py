from bocadillo import App, view, provider

app = App(enable_sessions=True)


@provider(scope="app", name="todos")
def provide_todos():
    return [
        {"id": 0, "content": "Go shopping"},
        {"id": 1, "content": "Cook fries"},
        {"id": 2, "content": "Do laundry"},
    ]


@app.route("/unseen-todos")
async def get_unseen_todos(req, res, todos):
    last_id = req.session.get("last_id", -1)
    unseen_todos = todos[last_id + 1 :]

    if unseen_todos:
        req.session["last_id"] = unseen_todos[-1]["id"]

    res.media = unseen_todos


@app.route("/todos")
@view(methods=["post"])
async def create_todo(req, res, todos):
    json = await req.json()
    todo = {"id": len(todos) + 1, "content": json["content"]}
    todos.append(todo)
    res.status_code = 201


if __name__ == "__main__":
    app.run()
