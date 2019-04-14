# Redirecting

Inside a view, you can redirect to another URL by raising a `Redirect` exception. The given URL can be internal (a path relative to the server's host) or external (absolute URL).

```python
from bocadillo import Redirect

@app.route('/')
async def index(req, res):
    # internal:
    raise Redirect("/home")
    # external:
    raise Redirect("http://localhost:8000/home")
```

Redirections are temporary (302) by default. To return a permanent (301) redirection, pass `permanent = True`:

```python
raise Redirect("/home", permanent=True)
```
