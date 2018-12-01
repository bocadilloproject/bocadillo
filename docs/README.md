---
home: true
actionText: Get Started →
actionLink: /getting-started/
features:
- title: Simple and productive
  details: A minimal setup and carefully chosen included batteries help you solve common (and more advanced) problems in no time. 
- title: Async-first
  details: Embrace modern Python asynchronous programming capabilities! Don't worry, though — it's all optional.
- title: Performant
  details: Built on Starlette and Uvicorn, the lightning-fast Python ASGI toolkit and server.
- title: Progressive
  details: Bocadillo has extensions for useful features that not everyone might need, like talking to a database.
- title: Developer-friendly
  details: Use Bocadillo CLI to generate code or perform management operations in a breeze.
- title: Familiar
  details: Ever used Django, Flask or Falcon? You'll feel comfortable here.
footer: MIT Licensed | Copyright © 2018-present Florimond Manca
---

## Quick start

Install it:

```bash
pip install bocadillo
```

Build something:

```python
# api.py
import bocadillo

api = bocadillo.API()

@api.route('/')
async def index(req, res):
    res.html = await api.template('index.html')

@api.route('/greet/{person}')
def greet(req, res, person):
    res.media = {'message': f'Hi, {person}!'}

if __name__ == '__main__':
    api.run()
```

Launch:

```bash
python api.py
```

Make requests!

```bash
curl http://localhost:8000/greet/Bocadillo
{"message": "Hi, Bocadillo!"}
```

Hungry for more? [Read the guide](/guide/) to get started.
