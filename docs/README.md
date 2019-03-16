---
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

Install it:

```bash
pip install bocadillo
```

Build something:

```python
# app.py
from bocadillo import App, Templates

app = App()
templates = Templates(app)

@app.route("/")
async def index(req, res):
    # Use a template from the ./templates directory
    res.html = await templates.render("index.html")

@app.route("/greet/{person}")
async def greet(req, res, person):
    res.media = {"message": f"Hi, {person}!"}

if __name__ == "__main__":
    app.run()
```

Launch:

```bash
python app.py
```

Make requests!

```bash
curl http://localhost:8000/greet/Bocadillo
{"message": "Hi, Bocadillo!"}
```

Hungry for more? Head to our [Getting Started](./getting-started/README.md) guide!
