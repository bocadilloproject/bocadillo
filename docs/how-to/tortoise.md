# Use Tortoise ORM to interact with an SQL database

[Tortoise ORM][tortoise] is a promising asynchronous Python ORM that allows you to interact with an SQL database asynchronously using a Django-like API. This guide will take you through the steps of integrating it into a Bocadillo application.

For more background, see our [discussion on databases][databases-discussion].

::: warning
Tortoise ORM is still a rather young project. As such, some convenient features like database migrations are not supported _yet_. See also their [roadmap][tortoise-roadmap].
:::

## Instructions

1. Install Tortoise itself:

```bash
pip install tortoise-orm
```

2. Tortoise comes with [aiosqlite] by default, but if you're using another database than SQLite, install the adequate async driver among [those supported by Tortoise][tortoise-db-backends], e.g. [asyncpg]:

```bash
pip install asyncpg
```

3. Register startup and shutdown [event handlers][events] to initialize and clean up database connection (see also [Set up (Tortoise)][tortoise-setup]):

```python
from bocadillo import App
from tortoise import Tortoise

app = App()


@app.on("startup")
async def db_init():
    await Tortoise.init(
        # Connect to a database located at `$DATABASE_URL`,
        db_url=os.environ["DATABASE_URL"],
        # Register the `models.py` file to be discovered for models.
        # The name of the module will be used as a namespace when
        # referencing models, e.g. when setting up relationships.
        modules={"models": ["models"]}
    )
    # Generate the schema
    await Tortoise.generate_schemas()


@app.on("shutdown")
async def db_cleanup():
    await Tortoise.close_connections()
```

That's it! You can now [write models][tortoise-models] and [make queries][tortoise-queries] as described in the official documentation.

For an alternative introduction to Tortoise, follow the [Tortoise Getting Started guide][tortoise-getting-started].

## Bloguero: a blog example

Bloguero is an example blog app that makes use of Tortoise to store blog posts.

The full code for Bloguero can be found [on GitHub][bloguero], but we'll go through some key concepts here.

First, we define a `Post` model, i.e. a class that derives from `tortoise.models.Model` and declares a database fields.

```python
# models.py
from tortoise.models import Model
from tortoise import fields

class Post(Model):
    title = fields.CharField(max_length=80)
    content = fields.TextField()
    category = fields.ForeignKeyField("models.Category", related_name="posts")

    def __str__(self):
        return self.title
```

As you can see, the API is very similar to that of the Django ORM.

The `category` field is special — it is a one-to-many (foreign key) relationship with the `Category` model below.

```python
# models.py
class Category(Model):
    name = fields.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
```

In `"models.Category"`, `"models"` is the name we gave to the Tortoise module which has `models.py` registered in discovery — that was in the init event handler, remember?

```python
await Tortoise.init(
        # ...
        modules={"models": ["models"]}
    )
```

Plus, `related_name` defines how all posts of a category can be accessed. Here, passing `"posts"` means we can query a category's posts using `async for category.posts: ...`.

For a thorough description of the foreign key field and many others, see the [Tortoise fields reference][tortoise-fields].

Now that these models are defined in the `models.py` file, we can create the main application script, e.g. `blog.py`, add the Tortoise integration script there and start writing views:

```python
from bocadillo import App
from tortoise import Tortoise
from models import Post

app = App()

# << Tortoise integration code >>

@app.route("/")
async def home(req, res):
    # Fetch all posts along with their categories
    posts = await Post.all().prefetch_related("category")
    # Render a template that lists all posts
    res.html = await app.template("home.html", posts=posts)

# << More routes >>

if __name__ == "__main__":
    app.run()
```

Again, feel free to read through Bloguero's source code [on GitHub][bloguero] to understand the finer details and see the complete CRUD implementation.

[tortoise]: https://tortoise-orm.readthedocs.io
[databases-discussion]: ../discussions/databases.md
[aiosqlite]: https://github.com/jreese/aiosqlite
[events]: ../guides/agnostic/events.md
[asyncpg]: https://github.com/MagicStack/asyncpg
[tortoise-roadmap]: https://tortoise-orm.readthedocs.io/en/latest/roadmap.html
[tortoise-db-backends]: https://tortoise-orm.readthedocs.io/en/latest/index.html#pluggable-database-backends
[tortoise-setup]: https://tortoise-orm.readthedocs.io/en/latest/setup.html
[tortoise-models]: https://tortoise-orm.readthedocs.io/en/latest/models.html
[tortoise-queries]: https://tortoise-orm.readthedocs.io/en/latest/query.html
[tortoise-getting-started]: https://tortoise-orm.readthedocs.io/en/latest/getting_started.html
[tortoise-fields]: https://tortoise-orm.readthedocs.io/en/latest/fields.html
[bloguero]: https://github.com/bocadilloproject/bloguero
