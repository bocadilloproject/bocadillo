# Auto-used providers

Sometimes, you may want a provider to be provisioned without having to explicitly declare it as a parameter in your views.

In that case, you can pass `autouse=True` to the provider, and it will be automatically activated (within its configured scope).

Such providers are called **auto-used providers**.

## Example: automatically entering a database transaction

Suppose you're using [Databases](https://github.com/encode/databases) as an async database library, and you want to make sure that database calls in views are performed within a transaction.

This is a situation in which an auto-used provider would shine:

```python
from databases import Database
from bocadillo import App, provider

from myapp.tables import notes  # imaginary

@provider(scope="app")
async def db() -> Database:
    async with Database("sqlite://:memory:") as db:
        yield db

@provider(autouse=True)
async def transaction(db: Database):
    async with db.transaction():
        yield

app = App()

@app.route("/")
async def index(req, res, db: Database):
    # This query is being executed within a transaction. ✨
    res.json = await db.fetch_all(notes.select())
```
