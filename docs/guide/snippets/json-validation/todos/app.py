# todos/app.py
from bocadillo import App
from .models import Todo

app = App()


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
