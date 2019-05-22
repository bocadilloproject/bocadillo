# Use `orm` to interact with an SQL database

The [orm] ilbrary is a Python asynchronous ORM. We've discussed what ORMs are in the [Databases](/discussions/databases.md) guide. This page will show you how to integrate it in a Bocadillo project in order to retrieve, validate and insert data into an SQL database.

[orm]: https://github.com/encode/orm

We'll be working on a `blog` project generated with the [Bocadillo CLI](https://github.com/bocadilloproject/bocadillo-cli).

## Setup

1. Install `orm`. It's still a young project, so make sure to pin your dependencies to avoid breaking changes!

```bash
pip install "orm>=0.1,<0.2"
```

2. Configure the database URL in the [settings module](/guide/config.md#settings-module):

```python
# blog/settings.py
from starlette.config import Config
from starlette.datastructures import URL

config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=URL)
```

3. In a `models.py` module, configure the database and declare a `Post` model to represent blog posts:

```python
# blog/models.py
import os

# All these come installed with `orm`.
import databases
import orm
import sqlalchemy

from . import settings

database = databases.Database(str(settings.DATABASE_URL))
metadata = sqlalchemy.MetaData()

class Post(orm.Model):
    __tablename__ = "posts"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    title = orm.String(max_length=300)
    content = orm.Text(allow_blank=True)

engine = sqlalchemy.create_engine(str(settings.DATABASE_URL))
metadata.create_all(engine)
```

4. [Provide](/guide/providers.md) a database connection:

```python
# blog/providerconf.py
from bocadillo import provider
from .models import database

@provider(scope="app")
async def db():
    async with database:
        yield database
```

## Making queries

Once we've done the above, we can import the `Post` model in order to make queries to the database.

For example, let's add a route `GET /posts` to return the list of all blog posts:

```python
# blog/app.py
from bocadillo import App, discover_providers
from .models import Post

app = App()
discover_providers("blog.providerconf")

@app.route("/posts")
class TodoList:
    async def get(self, req, res):
        res.json = [dict(post) for post in await Post.objects.all()]
```

To learn more about making queries with `orm`, you can read the [orm documentation][orm].

## Data validation

`orm` models are [TypeSystem] schemas themselves, which means we get **data validation for free!**

[typesystem]: https://www.encode.io/typesystem

More specifically, data passed to `.create()` and `.update()` is validated against the model's fields, and calling these methods may raise a `typesystem.ValidationError` exception.

Thanks to [JSON validation](/guide/json-validation.md), Bocadillo is able to catch and process this exception in order to return an appropriate error response.

This eliminates boilerplate and allows you to write clean REST API endpoints. ✨

As an example, let's extend the `/posts` endpoint to allow users to create a blog post:

```python{13,14,15}
# blog/app.py
from bocadillo import App, discover_providers
from .models import Post

app = App()
discover_providers("blog.providerconf")

@app.route("/posts")
class TodoList:
    async def get(self, req, res):
        res.json = [dict(post) for post in await Post.objects.all()]

    async def post(self, req, res):
        todo = await Todo.objects.create(**await req.json())
        res.json = dict(todo)
```

Since we call `Todo.objects.create()` in `.post()`, the input JSON is validated against the `Post` model's data schema, and Bocadillo will return a `400 Bad Request` error response if it is invalid.
