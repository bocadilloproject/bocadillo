---
home: true
layout: HomeLayout
heroText: Bocadillo
tagline: Fast, scalable and real-time capable web APIs for everyone
metaTitle: "Bocadillo | Python async web framework"
heroImage: /logo.png
actionText: Get Started →
actionLink: /guide/
footer: MIT Licensed | Copyright © 2018-present Florimond Manca
---

## What is Bocadillo?

**Bocadillo** is a **Python asynchronous and ASGI web framework** that makes building performant and highly concurrent web APIs fun and accessible to everyone.

<b-features :summary="true"/>

<b-action-link to="/guide/" text="Learn more about Bocadillo" :primary="false"/>

## Requirements

Python 3.6+

## Installation

```bash
pip install bocadillo
```

## Example

```python
from bocadillo import App, configure

app = App()
configure(app)

@app.route("/")
async def index(req, res):
    res.json = {"hello": "world"}
```

Save this as `app.py`, then start a [uvicorn](https://www.uvicorn.org) server (hot reload enabled!):

```bash
uvicorn app:app --reload
```

Say hello!

```bash
$ curl http://localhost:8000
{"hello": "world"}
```

Ready to dive in?

<b-action-link to="/guide/tutorial" text="Read the tutorial →"/>
