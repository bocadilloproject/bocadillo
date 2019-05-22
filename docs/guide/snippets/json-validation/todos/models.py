import typesystem


class Todo(typesystem.Schema):
    title = typesystem.String(max_length=20)
    done = typesystem.Boolean(default=False)
