# Use Tortoise ORM to interact with an SQL database

Relational databases are a robust, well-established and convenient way to
persist and query application data.

[Tortoise ORM][tortoise] is a promising asynchronous Python ORM that allows you to interact with an SQL database asynchronously using a Django-like API.

::: warning
Tortoise ORM is still a rather young project. As such, some convenient features like database migrations are not supported *yet*. See also their [roadmap][tortoise-roadmap].
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
from bocadillo import API
from tortoise import Tortoise

api = API()


@api.on("startup")
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


@api.on("shutdown")
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
from bocadillo import API
from tortoise import Tortoise
from models import Post

api = API()

# << Tortoise integration code >>

@api.route("/")
async def home(req, res):
    # Fetch all posts along with their categories
    posts = await Post.all().prefetch_related("category")
    # Render a template that lists all posts
    res.html = await api.template("home.html", posts=posts)

# << More routes >>

if __name__ == "__main__":
    api.run()
```

Again, feel free to read through Bloguero's source code [on GitHub][bloguero] to understand the finer details and see the complete CRUD implementation.

## Discussion

### What is an ORM?

Paraphrasing the [Wikipedia page][orm-wikipedia], ORM — a.k.a. *Object Relational Mapping* — is a programming technique to convert data between incompatible type systems.

Although it is a general concept, *an ORM* typically refers to software that acts as **a conversion layer between a given programming language and a database**, e.g. between Python and PostgreSQL.

Put simply, an ORM allows the developer to interact with the database through objects and method calls instead of writing SQL queries by hand.

### Do I need an ORM?

Using an ORM has the benefit of making the data manipulation code more reusable, more consistent and more secure.

That said, keep in mind that ORMs have downsides, too. [Full Stack Python's article on Object Relation Mappers][fsp-article] mentions impedance mismatch, potentially reduced performance, and shift of complexity from the database to application code.

Depending on your use case, you may get away with using an async SQL client such as:

- [asyncpg] for PostgreSQL.
- [aiomysql] for MySQL.
- [aiosqlite] for SQLite.

### Why not SQLAlchemy?

[SQLAlchemy] is a very popular Python ORM, commonly used in conjonction with a microframework such as [Flask], [Falcon] or similar.

The main issue with SQLAlchemy in the context of asynchronous web servers is that it is *synchronous*. This means that while the query is being executed, the server will block while it is waiting on I/O.

In fact, querying a database is almost always an I/O-bound operation. This makes asynchronous programming a very suitable paradigm for interacting with databases.

### Why Tortoise ORM?

Because it is async-first, just like Bocadillo.

Implementations of async Python ORMs rely on the recent development of async Python database clients (such as [asyncpg] or [aiomysql]).

A popular approach has been to map synchronous ORMs to be asynchronous. This is the case of [GINO][gino], built on top of SQLAlchemy Core, or [peewee-async], built on top of [peewee].

On the other hand, [Tortoise ORM][tortoise] is a from-scratch ORM implementation specifically targeted at async Python applications. It exposes a clean API very reminiscent of the Django ORM.

### What about NoSQL?

If you're using NoSQL, you don't need an ORM and — luckily — many high-quality async clients are already available, such as:

- [Motor] for MongoDB.
- [aioelasticsearch] for ElasticSearch.
- [aioredis] for Redis.

[orm-wikipedia]: https://en.wikipedia.org/wiki/Object-relational_mapping
[fsp-article]: https://www.fullstackpython.com/object-relational-mappers-orms.html
[flask]: http://flask.pocoo.org
[falcon]: https://falcon.readthedocs.io
[sqlalchemy]: https://www.sqlalchemy.org
[asyncpg]: https://www.github.com/MagicStack/asyncpg
[aiomysql]: https://github.com/aio-libs/aiomysql
[aiosqlite]: https://github.com/jreese/aiosqlite
[gino]: https://github.com/fantix/gino
[peewee-async]: https://github.com/05bit/peewee-async
[peewee]: https://github.com/coleifer/peewee
[motor]: https://github.com/mongodb/motor
[aioelasticsearch]: https://github.com/aio-libs/aioelasticsearch
[aioredis]: https://github.com/aio-libs/aioredis
[events]: ../guides/agnostic/events.md
[bloguero]: https://github.com/bocadilloproject/bloguero
[tortoise]: https://tortoise-orm.readthedocs.io/en/latest/
[tortoise-db-backends]: https://tortoise-orm.readthedocs.io/en/latest/index.html#pluggable-database-backends
[tortoise-setup]: https://tortoise-orm.readthedocs.io/en/latest/setup.html
[tortoise-roadmap]: https://tortoise-orm.readthedocs.io/en/latest/roadmap.html
[tortoise-models]: https://tortoise-orm.readthedocs.io/en/latest/models.html
[tortoise-queries]: https://tortoise-orm.readthedocs.io/en/latest/query.html
[tortoise-getting-started]: https://tortoise-orm.readthedocs.io/en/latest/getting_started.html
[tortoise-fields]: https://tortoise-orm.readthedocs.io/en/latest/fields.html
