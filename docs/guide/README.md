# Introduction

Hi there, and welcome to the Bocadillo documentation! 👋

Before we get started, here is some general information about Bocadillo we thought you may want to know.

In a hurry? Skip to [Installation](/guide/installation.md).

## About this website

This documentation site is an ongoing community effort. If you find a typo, use the "Edit" link at the bottom of each page to submit a fix!

## What is Bocadillo?

Bocadillo is a Python async web framework that makes building performant and highly concurrent web apps fun and accessible to everyone.

It is designed to be:

- **Productive**: a carefully chosen set of included batteries helps you solve common and more advanced problems.
- **Real-time capable**: embrace Python 3.6+ asynchronous programming and the baked-in [WebSocket] and [SSE] support to build real-time, highly-concurrent systems.
- **Flexible**: inject resources into web views using [providers], an explicit, modular and easy-to-use mechanism inspired by pytest fixtures.
- **Performant**: Bocadillo is built on top of [Starlette] and [uvicorn], the lightning-fast ASGI toolkit and web server.
- **Empowering**: ships with testing and development tools that help you build delicious, high-quality applications.
- **Transparent**: we make sure every single feature is documented front to back, and provide optimal editor support with a 100% type-annotated code base.

[websocket]: /guide/websockets.md
[sse]: /guide/sse.md
[providers]: /guide/providers.md
[starlette]: https://www.starlette.io
[testing]: /guide/testing.md

## What makes Bocadillo an async web framework?

Historically, web frameworks in the Python ecosystem — Django, Flask, Pyramid, Falcon, etc. — have been built using the [WSGI] standard. WSGI is a **common language** that Python web servers (such as [gunicorn]) and web applications use to communicate.

[wsgi]: https://www.python.org/dev/peps/pep-3333/
[gunicorn]: https://gunicorn.org

Yet, WSGI was not designed for concurrency. It can only handle one request at a time. As a result, if processing a request requires running a 10-second long database query, other clients have to wait, period.

This is why, after the introduction of asynchronous programming in Python 3.5 ([async/await], [asyncio], etc), the community worked towards a new standard. The result of this effort was [ASGI] - the Asynchronous Server Gateway Interface.

[async/await]: https://www.python.org/dev/peps/pep-0492/
[asyncio]: https://docs.python.org/3/library/asyncio.html
[asgi]: https://asgi.readthedocs.io

Just like WSGI, **ASGI is a common language** that enables communication between _asynchronous_ web servers (such as [uvicorn]) and _asynchronous_ web applications (such as Bocadillo). This is similar to how HTTP makes the communication between web browsers and web servers possible.

[uvicorn]: https://www.uvicorn.org

<b-figure src="/asgi.png" caption="The flow of requests from a web browser to a Bocadillo application."/>

In short, **Bocadillo is an async web framework because it speaks the ASGI language**.

This has a number of benefits. Among others, you can now build **highly-concurrent web apps and services**, which typically results in **higher throughput** for applications that spend a lot of time on I/O.

## Do I need to use async?

**Yes**, you will need to use asynchronous programming to write Bocadillo applications.

We think this decision was totally worth it, because:

- It's **why you are here** — and why you didn't use a WSGI framework like Flask or Django in the first place.
- It's **faster**: internally, Bocadillo must deal with async functions anyway (because _async is all-in_), so supporting synchronous APIs would have reduced performance.
- It's **enriching**: we believe this is a great opportunity to level-up your Python async skills!

## I'm new to async. Where can I get help?

Although Bocadillo was designed to make working with async as pleasurable as possible, we do know that learning async Python can be overwhelming in the beginning.

If you need help to get the ground running, take a look at our [Async crash course](/guide/async.md).

## Why Bocadillo?

That's a great question! To learn more about the framework's history, design decisions, or why it's called Bocadillo in the first place, check out our [Frequently Asked Questions](/faq.md) page.
