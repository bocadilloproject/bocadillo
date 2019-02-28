# Testing

Bocadillo provides a few helpers to help you write great tests and ensure the quality of your apps.

This guide makes use of [pytest] as a testing framework, but the code should be easy to port to other testing frameworks such as [unittest].

[pytest]: https://pytest.org
[unittest]: https://docs.python.org/3/library/unittest.html

## Example app

As support material, here is an example application that allows to save books to a JSON file and list them. Reading from and writing to the file is performed using [aiofiles](https://github.com/Tinche/aiofiles).

```python
# books.py
import aiofiles

class BookStore(JSONFileStore):
    def __init__(self, filename: str):
        self.filename = filename
        self._last_id = 0

    async def _load(self) -> list:
        async with aiofiles.open(self.filename, "r") as f:
            return json.loads(await f.read())

    async def _dump(self, data):
        async with aiofiles.open(self.filename, "w") as f:
            f.write(json.dumps(books))

    async def save(self, book: dict):
        books = await self._load()
        books[book["id"]] = book
        await self._dump(books)

    async def add(self, title: str, content: str) -> dict:
        self._last_id += 1
        book = {"id": self._last_id, "title": title, "content": content}
        await self.save(book)
        return book

    async def all(self) -> list:
        books = await self._load()
        return list(books.values())
```

```python
# app.py
from bocadillo import App
from books import BookStore

app = App()
books = BookStore("books.json")

@app.route("/books")
class BooksView:
    async def get(self, req, res):
        res.media = await books.all()

    async def post(self, req, res):
        json = await req.json()
        try:
            book = await books.add(title=json["title"], content=json["content"])
        except KeyError as exc:
            field = exc.args[0]
            raise HTTPError(400, detail=f"{field}: this field is required.")
        else:
            res.media = book

if __name__ == "__main__":
    app.run()
```

## Test client

Every instance of [`App`](./app.md) ships with an instance of a [Starlette `TestClient`][testclient] stored under the `.client` attribute.

[testclient]: https://www.starlette.io/testclient/

The test client allows to make requests to the application using the same interface as the standard [requests](http://docs.python-requests.org/en/master/) library. It also supports connecting to WebSocket endpoints.

For example, here's how to make a GET request to your application:

```python
response = app.client.get("/some/endpoint")
```

We recommend you read the documentation for [`TestClient`][testclient] in the Starlette docs for reference.

## Testability patterns

The design patterns described here aim can be useful to improve the testability of your apps.

### Using environment variables

Using environment variables is a good way to make your application configurable.

For example, instead of hardcoding the file location of the book store, you could retrieve it from an environment variable as follows:

```python
# app.py
import os
from bocadillo import App

app = App()
books = BookStore(filename=os.getenv("BOOK_STORE_FILE", "books.json"))
```

During tests, you can override the `BOOK_STORE_FILE` environment variable so that books created during tests are stored in a separate file.

For example, this is how you could do it using pytest:

```python
# tests.py
from contextlib import contextmanager, FileNotFoundError
import pytest
from app import app

@contextmanager
def override_env(name, value):
    initial = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        os.environ.pop(name, None)
        if initial is not None:
            os.environ[name] = value

@pytest.fixture(autouse=True)
def setup_book_store_file():
    filename = "test_books.json"
    with override_env("BOOK_STORE_FILE", filename):
        yield

def test_something():
    ...
```

### Application factory

An application factory is a function that returns an application instance. It should be given instances of its dependencies so that non-production instances can be passed when testing.

For example, let's refactor the application script to use an application factory:

```python
# app.py
from bocadillo import App
from books import BookStore

def create_app(books: BookStore):
    app = App()

    @app.route("/books")
    class BooksView:
        ...

    return app

if __name__ == "__main__":
    books = BookStore("books.json")
    app = create_app(books)
```

As you can see, the book store is _injected_ into the factory. During tests, we can pass a store that stores books in a different JSON file:

```python
# tests.py
import pytest
from app import create_app

@pytest.fixture
def app():
    books = BookStore("test_books.json")
    return create_app(books)

def test_list_books(app):
    response = app.client.get("/books")
    assert response.status_code == 200
```
