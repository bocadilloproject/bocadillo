---
title: "Bocadillo 0.13 released!"
description: "This release represents an important milestone for Bocadillo: it brings a pack of new exciting features, including providers, SSE support and cookie-based sessions. Here's a summary of what's new."
date: 2019-03-16
author: Florimond Manca
layout: Post
---

[[toc]]

## Upgrade instructions

This release removes items that were deprecated by the 0.12.0 release:

- The `API` class no longer exists — use [`App`](/api/applications.md#app) instead!
- `App` instances no longer have the `.template()`, `.template_sync()` and `.template_string()` methods. Instead, use the [`Templates`](/api/templates.md#templates) helper.

All 0.12.x releases are compatible with these new APIs. If you're not up to date yet, I recommend you update your apps while staying under 0.12.x, and only then upgrade to 0.13.

Once you're ready to upgrade, you can grab the new version from [PyPI](https://pypi.org/project/bocadillo/0.13.0):

```python
pip install -U bocadillo
```

If you have any questions, feel free to [get in touch](/faq.md#getting-in-touch)!

## Providers: dependency injection for web views

[Providers] is a new powerful dependency injection mechanism baked right into Bocadillo.

[providers]: /guides/injection/

What they allow to do is **inject resources into web views**. This is done by declaring providers as function parameters, much in the style of [pytest fixtures](https://docs.pytest.org/en/latest/fixture.html). 🙌

Besides being very easy to use, I think that providers:

- Help build applications that are **easy to test, change and maintain**.
- Make the development experience much more enjoyable.

They're quite a big deal, so let's review them more in depth, shall we?

### Hello, providers!

Here's the mandatory "Hello, world" example:

```python
# providerconf.py
from bocadillo import provider

@provider
def hello():
    return "Hello, world!"
```

```python
# app.py
from bocadillo import App

app = App()

@app.route("/")
async def index(req, res, hello):  # <- ✨
    res.text = hello

if __name__ == "__main__":
    app.run()
```

### Motivation and design

Up to now, there was no elegant way to abstract logic into reusable services without resorting to global variables or similar hacks. This often led to cluttered, hard-to-test code, and ultimately impaired the usability of Bocadillo as a web framework.

To solve this, providers were designed to be:

- **Explicit**: it's clear which views use which resources.
- **Modular**: providers can use other providers, allowing to build an ecosystem of reusable components.
- **Flexible**: providers support a variety of syntaxes (sync/async, function/generator) and scopes (request or app), making them suitable for a wide range of use cases.

Besides, providers can be overridden at anytime, thus improving testability.

We extracted the core of this feature into [aiodine](https://github.com/bocadilloproject/aiodine), an async-first dependency injection library. Be sure to check it out!

### Next steps

Providers are a major addition to Bocadillo indeed, and quite a unique feature in the Python web framework space! If you can't wait to try them out, head to the docs: [Introduction to providers][providers].

## Server-Sent Event support

You may already be familiar with WebSocket — Bocadillo has had built-in support for them since v0.9.

This release pushes the real-time capabilities of Bocadillo even further by introducing support for [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events). This technique can be used to cheaply stream events from the server to the client, and build systems such as notifications or live-updating feeds.

Because this builds upon [response streaming](/guides/http/responses.md#streaming), you can very easily obtain those events from an external source — such as a [message queue](https://github.com/Polyconseil/aioamqp) or a [message broker](https://github.com/aio-libs/aiokafka).

Everything you need to know is in the [SSE usage guide](/guides/http/sse.md), but here's a sneak peak to get you going:

<<<@/docs/blog/snippets/release_0_13_sse.py

## Cookie-based sessions

Signed cookie-based sessions have landed in Bocadillo! Thanks a lot to [@zgoda](https://github.com/bocadilloproject/bocadillo/pull/211) for helping bring this feature in.

Sessions allow you to persist data between requests from a given client. You can find an example as well as usage tips in the new [Sessions guide](/guides/http/sessions.md).

## Testing utilities

This release brings in new testing utilities that you can use to ensure the quality of your Bocadillo applications: [`create_client`](/api/testing.md#create-client) and [`LiveServer`](/api/testing.md#liveserver).

We also wrote a brand new [Testing guide](/guides/architecture/testing.md) as well as a [pytest how-to guide](/how-to/test-pytest.md) to help you get started with Bocadillo testing! ✅

## Chatbot tutorial

To showcase the real-time capabilities of Bocadillo as well as the new providers feature, the "Getting started" section of the docs got an overhaul.

In particular, there's a brand new [tutorial](/getting-started/tutorial.md). There, you'll learn how to build a chatbot server using [ChatterBot](https://chatterbot.readthedocs.io/en/stable/) and WebSocket. 🤖

## Miscellaneous

### Middleware improvements

- The new [`ASGIMiddleware`](/how-to/middleware.md#using-the-asgimiddleware-base-class) base class streamlines the writing of ASGI middleware.
- HTTP middleware classes can now expect both the `inner` middleware _and_ the `app` instance to be passed to the constructor, instead of only `inner`. This allows to perform initialisation on the `app` by overriding the constructor. The same goes for the new `ASGIMiddleware` base class. See [Configuration and initialization](/how-to/middleware.md#configuration-and-initialization).
- Fix: ASGI middleware is now properly applied even when the request is routed to a sub-application (e.g. a recipe). In the past, this could lead to CORS headers not being added on a recipe despite them being configured on the root application.

### Streaming

- Fix: stream responses (and SSE streams by extension) now stop as soon as a client disconnects.
