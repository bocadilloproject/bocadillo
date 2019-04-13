# Deployment

In development, running the `app.py` application script has the effect of passing your ASGI application to [Uvicorn], a very fast ASGI server running on [uvloop], an event loop [up to 4x faster](https://github.com/MagicStack/uvloop#performance) than the standard [asyncio] event loop.

[uvicorn]: https://www.uvicorn.org
[uvloop]: https://github.com/MagicStack/uvloop
[asyncio]: https://docs.python.org/3/library/asyncio.html

In production you'll probably also want to use a process manager to be able to spin up multiple workers and increase throughput.

You'll also want to turn off [debug mode](/guides/app.md#debug-mode) to disable auto-reload and prevent displaying error tracebacks in the browser.

## Running with Gunicorn

[Gunicorn](https://gunicorn.org/) is a very popular option to manage multiple application processes in production. Luckily, uvicorn includes a worker class which means you can run your Bocadillo apps on Gunicorn with very little configuration (see also [Uvicorn Deployment](https://www.uvicorn.org/deployment/)).

The following will start a Gunicorn server for your application:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b localhost:8000 app:app
```

Let's break down this command:

1. `gunicorn`: this is the Gunicorn executable, which can be installed via `pip install gunicorn`
2. `-w 4`: Gunicorn will start and manage 4 application processes (a.k.a workers).
3. `-k uvicorn.workers.UvicornWorker`: here we pass Uvicorn's worker class
4. `-b localhost:8000`: specifies on which host and port the application should run.
5. `app:app`: identifies the Bocadillo application in the `path.to.module:object` format.

## Running with Docker

Bocadillo applications can easily be containerized to run in Docker containers. You can find an example `Dockerfile` in our [docker-example](https://github.com/bocadilloproject/docker-example) repo.

## What about static files?

A typical answer to, "How should I service static files for my Gunicorn-served web app" is that you should use a reverse proxy such as Nginx. Even though this and other options such as using a CDN or object storage are valid approaches, they're difficult to get started with and require extra sysadmin work.

Bocadillo keeps it simple by using [WhiteNoise](http://whitenoise.evans.io/en/stable/), a library that allows your application to serve its own static files in a simple and [performant enough](http://whitenoise.evans.io/en/stable/#infrequently-asked-questions) manner, making it self-contained — and ready to be deployed on managed platforms.

In practice, this means that **you won't need any extra steps to serve static files in production**, unless you have very high performance requirements, in which case you should probably put your app behind a CDN.

## Deployment solutions

### Heroku

Bocadillo applications are very easy to deploy to Heroku. Check out our [Heroku deployment guide](/how-to/heroku.md) to get started!
