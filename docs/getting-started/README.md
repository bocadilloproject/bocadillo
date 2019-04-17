# Introduction

Welcome to Bocadillo's documentation!

We recommend you read this quick introduction before you get started with Bocadillo. It will hopefully answer some of your questions about the purpose and goals of Bocadillo, and what to expect from it.

If you want to jump right in, feel free to skip to the [Installation guide](installation.md).

::: tip CONTRIBUTING
Building and improving the documentation is an ongoing community effort. If you'd like to contribute, join us on <repo text="GitHub"/> or use the "Edit" link at the bottom of each page!
:::

## What is Bocadillo?

Bocadillo is a modern Python web framework that aims at **making async web apps and services fun to build and accessible to everyone**. We ultimately believe that web frameworks should be fun and easy to use while empowering the developer to make good decisions and ship high-quality applications.

### Design

Bocadillo is designed to be:

- **Productive**: a carefully chosen set of included batteries\* helps you solve common and more advanced problems.
- **Real-time capable**: embrace async programming and the baked-in [WebSocket] and [SSE] support to build real-time, highly-concurrent systems.
- **Flexible**: inject resources into web views using [providers], an explicit, modular and easy-to-use mechanism inspired by pytest fixtures.
- **Performant**: Bocadillo is built on top of [Starlette] and [uvicorn], the lightning-fast ASGI toolkit and framework.
- **Empowering**: ships with testing and development tools that help you build delicious, high-quality applications.
- **Transparent**: we make sure every single feature is documented front to back, and provide optimal editor support with a 100% type-annotated code base.

[websocket]: /guides/websockets/
[sse]: /guides/http/sse.md
[providers]: /guides/injection/
[starlette]: https://www.starlette.io
[testing]: /guides/architecture/testing.md

_\*The bucket list: HTTP, WebSocket, SSE, CORS, HSTS, GZip, [Jinja2] templates, background tasks, streaming, middleware, redirection, error handling, class-based views, view hooks, media responses, file responses, attachments, static files serving via [WhiteNoise], event handlers…_

[whitenoise]: http://whitenoise.evans.io
[jinja2]: http://jinja.pocoo.org

### An async web framework

We say Bocadillo is an _async_ web framework. What does that mean?

Historically, web frameworks in the Python ecosystem — Django, Flask, Pyramid, Falcon, etc. — have built upon the [WSGI] standard. WSGI is a **common language** that Python web servers (such as [gunicorn]) and web applications use to communicate.

[wsgi]: https://www.python.org/dev/peps/pep-3333/
[gunicorn]: https://gunicorn.org

WSGI was not designed to handle multiple clients at a time — a property known as concurrency. If processing a request requires running a 10-second long database query, other clients have to wait, period.

This is why, after the introduction of asynchronous programming in Python 3.5 ([async/await], [asyncio], etc), the community worked towards a new standard. The result of this effort is [ASGI] - the Asynchronous Server Gateway Interface.

[async/await]: https://www.python.org/dev/peps/pep-0492/
[asyncio]: https://docs.python.org/3/library/asyncio.html
[asgi]: https://asgi.readthedocs.io

Just like WSGI, **ASGI is a common language** that Python _asynchronous_ web servers (such as [uvicorn]) and _asynchronous_ web applications use to communicate. This is similar to how HTTP makes the communication between web browsers and web servers possible.

[uvicorn]: https://www.uvicorn.org

![](/asgi.png)

**Bocadillo is an async web framework because it speaks the ASGI language**. That's it! ✨

This has a number of benefits. Among others, you can now build **highly-concurrent web apps and services**, which typically results in **higher throughput** for applications that spend a lot of time on I/O.

### What if I don't do async?

If you're just getting started with asynchronous programming in Python, we thought you would find the following resources useful:

- [Asynchronous Python for the Complete Beginner](https://www.youtube.com/watch?v=iG6fr81xHKA) - Miguel Grinberg, PyCon 2017.
- [Async IO in Python: A Complete Walkthrough](https://realpython.com/async-io-python/) - Real Python.

Also check out the [awesome-asyncio] repo on GitHub to get a feel of what the Python async ecosystem has to offer.

[awesome-asyncio]: https://www.github.com/timofurrer/awesome-asyncio

If you don't particularly need to use async in some places, don't worry — Bocadillo is async-_first_, not async-_only_. This means that a lot of times writing asynchronous code is entirely optional, and Bocadillo will understand you just fine if you write plain ol' functions. But when you do need async and concurrent execution, be sure Bocadillo will have your back.

## Getting more background

To learn more about the framework's history, design decisions or why it's even called Bocadillo, check out our [Frequently Asked Questions][faq] page.

[faq]: ../faq/
