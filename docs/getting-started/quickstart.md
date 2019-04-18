# Quickstart

Now that you've got Bocadillo [installed][installation], let's go through the traditional "Hello, world!" example. The purpose of this example is to demonstrate a minimal application and to run it.

[installation]: ./installation.md

We'll use the [Bocadillo CLI] to generate a project. First, install it:

[bocadillo cli]: https://github.com/bocadilloproject/bocadillo-cli

```bash
pip install bocadillo-cli
```

Next, create a new project called `hello`:

```bash
bocadillo create hello
```

You can now `cd hello` and look around. Inside the `hello` package, a bunch of files were generated:

```
hello
├── __init__.py
├── app.py
├── asgi.py
├── providerconf.py
└── settings.py
```

Here's what each of them corresponds to:

- `app.py`: this is the [application](/guides/architecture/app.md) script. This is where you declare views and bind them to URLs.
- `asgi.py`: this is the ASGI server entry point, which we can pass to [uvicorn] to serve the application.
- `providerconf.py`: this is the configuration script for [providers](/guides/injection/), Bocadillo's powerful dependency injection mechanism for web views.
- `settings.py`: this is the [settings module](/guides/architecture/app.md#settings-module) which is used to configure the application.

[uvicorn]: https://www.uvicorn.org

You'll learn more about the associated features when reading the usage guides. For now, let's focus on the `app.py` script and add an HTTP route there:

```python{6,7,8}
# hello/app.py
from bocadillo import App

app = App()

@app.route("/")
async def index(req, res):
    res.text = "Hello, world!"
```

If you've ever worked with [Flask](http://flask.pocoo.org), the API should look familiar: we use the `@app.route()` decorator to tell Bocadillo to register the `index()` function at the root URL `/`. This operation is known as **routing**.

The `index()` function is a **view**. It is a coroutine function (hence the `async` keyword) that takes a request and a response as parameters, and mutates the response as required — a pattern borrowed from [Falcon](https://falconframework.org). Here, we send a plain text response.

We're now ready to start the server:

```bash
uvicorn hello.asgi:app
```

You can now head to [http://localhost:8000](http://localhost:8000), and see "Hello, world!" printed on your screen! :tada:

![](./hello-world.png)

This minimal hello world application is mostly done! If you already wonder how to deploy it to production, check out the [deployment guide](https://www.uvicorn.org/deployment/).

Carry on to the tutorial, in which we'll go on the journey of building a **chatbot server** with Bocadillo!
