# Modularity: using providers in providers

Providers are **modular** — they can be used in other providers too to build a loosely-coupled ecosystem of reusable resources.

## Basic example

Here's a very contrived example to show how this works:

```python
from bocadillo import App, provider

@provider
def message():
    return "hello"

@provider
def message_caps(message):
    return message.upper()

app = App()

@app.route("/")
async def index(req, res, message_caps):
    res.text = message_caps
```

## Example: reusable aiohttp session

As a more elaborate example, let's build a provider `aiohttp` client session and use that in another provider that needs to perform an HTTP call:

```python
import aiohttp
from bocadillo import App, provider

@provider
def http():
    async with aiohttp.ClientSession() as session:
        return session

@provider
async def random_json(http):
    async with http("https://httpbin.org/json") as resp:
        return await resp.json()

app = App()

@app.route("/data")
async def data(req, res, random_json):
    res.media = random_json
```

The good thing is that the `http` provider is **reusable** — you could reuse it in other providers of other views. This encourages writing small, focused providers and building more complex ones on top of them.
