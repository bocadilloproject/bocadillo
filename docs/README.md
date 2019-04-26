---
layout: HomePage
home: true
heroImage: /social-image.png
actionText: Get Started →
actionLink: /getting-started/
features:
  - title: 🥪 Productive
    details: A carefully chosen set of included batteries helps you solve common and more advanced problems.
  - title: 🧞‍ Real-time capable
    details: Embrace asynchronous programming and the baked-in WebSocket and SSE support to build real-time, highly-concurrent systems.
  - title: 🍬 Flexible
    details: Inject resources into web views using providers, an explicit, modular and easy-to-use mechanism inspired by pytest fixtures.
  - title: ⚡️ Performant
    details: Squeeze the juice out of Starlette and uvicorn, the lightning-fast ASGI toolkit and web server.
  - title: 👨‍🍳👩‍🍳 Empowering
    details: Use tailored testing and command line tools to build delicious, high-quality applications.
  - title: 👓 Transparent
    details: Every single feature is documented front to back and has optimal editor support thanks to a 100% type-annotated code base.
footer: MIT Licensed | Copyright © 2018-present Florimond Manca
meta:
  - name: twitter:title
    content: Bocadillo
  - name: twitter:description
    content: A modern Python web framework filled with asynchronous salsa
---

## Quick start

1. Install [Bocadillo] and the [Bocadillo CLI]:

```bash
pip install bocadillo bocadillo-cli
```

[bocadillo]: https://github.com/bocadilloproject/bocadillo
[bocadillo cli]: https://github.com/bocadilloproject/bocadillo-cli

2. Generate a project and `cd` into it:

```bash
bocadillo create hello
cd hello/
```

3. Edit the application script:

```python
# hello/app.py
from bocadillo import App

app = App()

@app.route("/")
async def index(req, res):
    res.text = "Hello, world!"
```

4. Start a [uvicorn] server (hot reload enabled!):

[uvicorn]: https://www.uvicorn.org

```bash
uvicorn hello.asgi:app --reload
```

5. Say hello!

```bash
$ curl http://localhost:8000
Hello, world!
```

6. Edit `app.py` to send "Hello, Bocadillo!" instead, then hit save. Uvicorn will pick up the changes and restart the application. Try it out again:

```bash
$ curl http://localhost:8000
Hello, Bocadillo!
```

Tastes good! 🥪

Hungry for more? Head to our [Getting Started](./getting-started/README.md) guide!
