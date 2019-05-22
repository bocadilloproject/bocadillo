# JSON validation

Bocadillo has built-in support for JSON data validation within views using [TypeSystem], a data validation library.

::: tip NOTE
If you're looking to validate data before saving it to a database, see [Data validation (ORM)](/how-to/orm.md#data-validation). If you are looking to validate arbitrary JSON objects, read on!
:::

[typesystem]: https://www.encode.io/typesystem/
[orm]: https://github.com/encode/orm

## How it works

JSON data validation is implemented by registering an [error handler](/guide/errors.md) for the `typesystem.ValidationError` exception.

Thanks to this, you can transparently use all the features of TypeSystem and **let validation fail** within views: Bocadillo will format and send a `400 Bad Request` error response for you.

::: tip
TypeSystem comes installed with Bocadillo, and this feature is enabled by default, so you can use it right out of the box. 🎉
:::

## Example

Consider a `todos` application.

1. In `models.py`, we define a `Todo` data schema.

<<<@/docs/guide/snippets/json-validation/todos/models.py

2. In `app.py`, we validate the JSON payload with the `Todo` schema and then create a todo item:

<<<@/docs/guide/snippets/json-validation/todos/app.py

Let's try it out:

1. Run the app using `$ uvicorn todos.asgi:app`.
2. Make a request with a valid JSON payload — everything should be fine:

```bash
$ curl \
  -X POST \
  -d '{"title": "Make breakfast"}' \
  http://localhost:8000/todos
```

```json
{
  "title": "Make breakfast",
  "done": false
}
```

- Send an invalid payload instead (e.g. title too long) — Bocadillo should automatically return an explicit error response:

```bash
$ curl \
  -X POST \
  -d '{"title": "Buy cornflakes at the store and make breakfast"}' \
  http://localhost:8000/todos
```

```json
{
  "error": "400 Bad Request",
  "status": 400,
  "detail": { "title": "Must have no more than 20 characters." }
}
```

This is a fairly basic example, but you can read the [TypeSystem documentation][typesystem] to learn about more complex validation techniques.

## Disabling validation error handling

If you wish to disable the `ValidationError` error handler, use the `HANDLE_TYPESYSTEM_VALIDATION_ERROR` setting:

```python
# myproject/settings.py
HANDLE_TYPESYSTEM_VALIDATION_ERROR = False
```

You would then have to handle `typesystem.ValidationError` yourself, or implement your own error handlers in case you want to use a different data validation library.
