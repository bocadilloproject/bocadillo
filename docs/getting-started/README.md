# Introduction

Hi there, and welcome to the Bocadillo documentation! 👋

This page is about the design of Bocadillo, and things you may want to know before diving in.

In a hurry? Skip to the [Installation guide](installation.md).

::: tip ABOUT THIS WEBSITE
This documentation site is an ongoing community effort. If you find a typo, use the "Edit" link at the bottom of each page to submit a fix!
:::

## What is Bocadillo?

Bocadillo is a **Python async web framework** that makes server-side async web apps **fun to build** and **accessible to everyone**.

::: tip
Migrating from v0.13.x? Read the [v0.14 release notes](/blog/release-0.14.html).
:::

### Design

Bocadillo is designed to be:

- **Productive**: a carefully chosen set of included batteries helps you solve common and more advanced problems.
- **Real-time capable**: embrace async programming and the baked-in [WebSocket] and [SSE] support to build real-time, highly-concurrent systems.
- **Flexible**: inject resources into web views using [providers], an explicit, modular and easy-to-use mechanism inspired by pytest fixtures.
- **Performant**: Bocadillo is built on top of [Starlette] and [uvicorn], the lightning-fast ASGI toolkit and web server.
- **Empowering**: ships with testing and development tools that help you build delicious, high-quality applications.
- **Transparent**: we make sure every single feature is documented front to back, and provide optimal editor support with a 100% type-annotated code base.

[websocket]: /guides/websockets/
[sse]: /guides/http/sse.md
[providers]: /guides/injection/
[starlette]: https://www.starlette.io
[testing]: /guides/architecture/testing.md

### An async web framework

We told you that Bocadillo is an _async_ web framework. What does that mean?

Historically, web frameworks in the Python ecosystem — Django, Flask, Pyramid, Falcon, etc. — have built upon the [WSGI] standard. WSGI is a **common language** that Python web servers (such as [gunicorn]) and web applications use to communicate.

[wsgi]: https://www.python.org/dev/peps/pep-3333/
[gunicorn]: https://gunicorn.org

WSGI was not designed to handle multiple clients at a time — a property known as **concurrency**. If processing a request requires running a 10-second long database query, other clients have to wait, period.

This is why, after the introduction of asynchronous programming in Python 3.5 ([async/await], [asyncio], etc), the community worked towards a new standard. The result of this effort was [ASGI] - the Asynchronous Server Gateway Interface.

[async/await]: https://www.python.org/dev/peps/pep-0492/
[asyncio]: https://docs.python.org/3/library/asyncio.html
[asgi]: https://asgi.readthedocs.io

Just like WSGI, **ASGI is a common language** that Python _asynchronous_ web servers (such as [uvicorn]) and _asynchronous_ web applications use to communicate. This is similar to how HTTP makes the communication between web browsers and web servers possible.

[uvicorn]: https://www.uvicorn.org

![](/asgi.png)

In short, **Bocadillo is an async web framework because it speaks the ASGI language**.

This has a number of benefits. Among others, you can now build **highly-concurrent web apps and services**, which typically results in **higher throughput** for applications that spend a lot of time on I/O.

### Do I need to use async?

**Yes**, you will need to use asynchronous programming to write Bocadillo applications.

Don't be afraid, though — it's totally worth it! Here's why:

- It's **why you are here** — and why you didn't use a WSGI framework like Flask or Django in the first place.
- It's **faster**: internally, Bocadillo must deal with async functions anyway (because _async is all-in_), so supporting synchronous APIs would have reduced performance.
- It's **enriching**: we believe this is a great opportunity to level-up your Python async skills!

### I'm new to async. Where can I get help?

We know that async Python can be confusing or overwhelming in the beginning.

If you need help to get the ground running, we recommend you read our [Async crash course](/guides/async.md).

## Getting more background

To learn more about the framework's history, design decisions or why it's even called Bocadillo, check out our [Frequently Asked Questions][faq] page.

[faq]: /faq.md
