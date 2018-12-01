# Middleware overview

::: warning
This feature is **experimental**; the middleware API may be subject to changes.
:::

Bocadillo provides a simple middleware architecture in the form of middleware classes.

## What are middleware classes?

Middleware classes provide behavior for the entire application. They act as an intermediate between the ASGI layer and the [API object]. In fact, they implement the [ASGI] protocol themselves.

## How middleware is applied

> TODO

## Using middleware

> TODO

[API object]: ../../api/api.md
[ASGI]: https://asgi.readthedocs.io
