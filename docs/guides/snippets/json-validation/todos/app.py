# todos/app.py
from bocadillo import App
import typesystem

app = App()


class Todo(typesystem.Schema):
    title = typesystem.String(max_length=20)
    done = typesystem.Boolean(default=False)


@app.route("/todos")
class TodoList:
    async def post(self, req, res):
        # NOTE: this may raise a `ValidationError` if the JSON
        # payload is invalid.
        # No need to try/except: the error handler will process
        # the exception for us!
        todo = Todo.validate(await req.json())

        # TODO: store todo item.

        res.json = dict(todo)
        res.status_code = 201
