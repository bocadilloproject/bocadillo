# Factory providers

Sometimes you want a provider to be generic so that it can be used for a variety of inputs.

**Factory providers** allow to do that: instead of having the provider function return a _value_, it returns a _function_.

::: tip NOTE
Factory provider is just a _pattern_. There's no magic performed behing the scenes: it's just a provider that provides a callable.
:::

## Example: parametrized database query

A good candidate for a factory provider would be a parametrized database query. For example, let's build a factory provider that retrieves an item from the database given its primary key.

The following example simulates that with a hardcoded, in-memory database of sticky notes:

```python
from bocadillo import App, provider

@provider(scope="app")
def notes():
    return [
        {"id": 1, "text": "Groceries"},
        {"id": 2, "text": "Make potatoe smash"},
    ]

@provider
def get_note(notes):
    async def _get_note(pk: int) -> list:
        try:
            # TODO: fetch from a database instead?
            return next(note for note in notes if note["id"] == pk)
        except StopIteration:
            raise HTTPError(404, detail=f"Note with ID {pk} does not exist.")

    return _get_note

app = App()

@app.route("/notes/{pk}")
async def retrieve_note(req, res, pk: int, get_note):
    res.media = await get_note(pk)
```

## Example: providing temporary files

This example allows views to create and access temporary files.

The factory provider pattern is combined with [provider cleanup](#cleaning-up-providers) so that temporary files are removed once the provider goes out of scope:

```python
import os
from bocadillo import provider

@provider
def tmpfile():
    files = set()

    async def _create_tmpfile(path: str):
        with open(path, "w") as tmp:
            files.add(path)
            return tmp

    yield _create_tmpfile

    for path in files:
        os.remove(path)
```
