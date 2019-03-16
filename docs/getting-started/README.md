# Introduction

Welcome to Bocadillo's documentation!

We recommend you read this quick introduction before you get started with Bocadillo. It will hopefully answer some of your questions about the purpose and goals of Bocadillo.

That said, if you want to jump right in, feel free to skip to the [Installation guide](installation.md).

::: warning STATUS NOTE
Bocadillo is still in **Alpha**. The documentation is regularly updated as new features are added and new guides are written. If you'd like to contribute, join us on <repo text="GitHub"/> or use the "Edit" link on each page of this site!
:::

## What is Bocadillo?

Bocadillo is a Python web framework that provides **a sane toolkit for quickly building performant web applications and services**, while encouraging best practices and keeping developer experience in mind.

Bocadillo is **fitted for a range of applications** — from REST APIs and microservices to database-backed web apps. It was designed to be **beginner-friendly** while giving power-users the ability to implement more advanced or complex behaviors.

Lastly, **Bocadillo is not exactly minimal**. It comes with a certain number of **included batteries** to help you solve common problems when building web apps: handling static files, providing API endpoints, rendering templates, and many more.

### Asynchronous-first

In typical WSGI frameworks (like Django, Flask or Falcon), the server is _synchronous_ — it is only able to process a single request at a time.

There are, however, times when the CPU will block and remain idle as it waits for an I/O-bound operation to execute — be it reading a file from disk, querying the database, sending an email, or performing an external HTTP request.

On the other hand, **Bocadillo is asynchronous at its core** — its main application object implements the [ASGI] protocol.

In simple words, this means that Bocadillo's server can **release the CPU during waiting periods** so that other tasks can use it, effectively resulting in **higher throughput** as Bocadillo deals with **multiple requests at once**.

<!-- Include a sequence diagram of WSGI vs ASGI -->

### What if I don't do async?

You may not be familiar with asynchronous programming in Python, or may not need to use it in your project — **that's perfectly fine!**

Indeed, while Bocadillo is async-first, **writing asynchronous code is entirely optional**. You can still write regular synchronous code like you've always done, if you prefer so; Bocadillo will still understand you.

However, be sure that Bocadillo has everything you need if you decide to embrace an asynchronous style of programming.

::: tip
As an introduction to asynchronous programming in Python, I strongly recommend you watch Miguel Grinberg's excellent talk [Asynchronous Python for the Complete Beginner](https://www.youtube.com/watch?v=iG6fr81xHKA) from PyCon 2017.
:::

## Why not…?

::: warning DISCLAIMER
All projects listed here are of great quality and absolutely deserve your attention.

The sole purpose of this section is for you to understand how Bocadillo differs from existing Python web frameworks.

Also, projects change and evolve. If you believe one of our claims has gone out of date, you are very welcome to tell us or submit a patch using the link at the bottom of this page.
:::

### Django

[Django] is probably the most popular Python web framework out there. It's got a huge community, great documentation and tons of features built-in.

However, Django also has a very steep learning curve. It's best suited for building large apps, so if you want to build simple web services, chances are Django will be too much.

Also, Django's only support for asynchronous Python is [Channels], which comes with its own set of abstractions and opinions, adding to the overall learning curve. Instead, Bocadillo's async-first approach makes writing async/await code a breeze, without any extra dependencies.

### Flask

[Flask] is a very popular Python microframework. It's got a very simple API and allows one to build apps very quickly.

Flask provides a simple core and lets the developer fully in control of the rest. However, this often results in relying on a lot of third-party extensions, which quickly becomes a burden.

On the other hand, Bocadillo keeps developer experience in mind and provides simple yet powerful tools to help you solve common (and more advanced) problems when building modern web applications and services.

Plus, as per Flask's [design decisions](http://flask.pocoo.org/docs/1.0/design/#design-decisions-in-flask), Flask "is just not designed for asynchronous servers" and "will never have a database layer". The latter is scheduled to be provided by Bocadillo.

### Falcon

[Falcon] is a fast, minimalist Python web framework specifically targeted at building backend services and APIs.

It's very good at what it does, but you'll have to do a fair amount of customization to use Falcon for anything else than REST APIs.

Plus, again, Falcon does not support async/await by itself (it officially recommends integrating with gevent).

### Responder

Kenneth Reitz says, "[Responder] is a mix between Flask/Falcon, but with ease of developer sanity kept in mind. Expect the Requests experience, but for building services" ([Oct. 2018](https://twitter.com/kennethreitz/status/1050723571004309505)).

Like Bocadillo, Responder borrows a lot of ideas from Flask and Falcon. It is also powered by the [Starlette] ASGI toolkit.

That said, some key differences between Responder and Bocadillo are:

- Responder's scope is smaller: it targets at web services (i.e. REST APIs) only.
- Its design is centered around the `API` class, while Bocadillo takes a more modular approach.
- Responder does not support middleware (but it has built-in GraphQL support).
- Bocadillo's documentation is, in our opinion, more thorough.
- It doesn't have a [CLI][queso].

## Features

Here's a sneak peak into what you'll find in Bocadillo:

- Core support for [async/await](https://docs.python.org/3/library/asyncio-task.html)
- Built upon the lightning-fast [Uvicorn] and [Starlette]
- WebSocket support
- Full HTTP support
- Decorator-based routing w/ parameter validation
- Falcon-style request/response manipulation and hooks
- Function- and class-based views
- In-app background tasks
- Efficient, zero-config static files handling powered by [WhiteNoise]
- [Jinja] template rendering
- Built-in CORS, GZip and HSTS support
- Streaming requests and responses
- [Queso], a customizable CLI built on top of [Click]

## Getting more background

To learn more about the framework's history, design decisions or why it's even called Bocadillo, check out our [Frequently Asked Questions][faq] page.

[asgi]: https://asgi.readthedocs.io
[django]: https://www.djangoproject.com
[channels]: https://channels.readthedocs.io
[flask]: http://flask.pocoo.org
[falcon]: https://falconframework.org
[responder]: http://python-responder.org/en/latest/
[starlette]: https://www.starlette.io
[uvicorn]: https://www.uvicorn.org
[whitenoise]: http://whitenoise.evans.io
[jinja]: http://jinja.pocoo.org
[click]: https://click.palletsprojects.com
[queso]: https://bocadilloproject.github.io/queso
[faq]: ../faq/
