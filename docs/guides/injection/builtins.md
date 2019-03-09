# Built-in providers

Bocadillo comes with a few built-in providers, which are listed here.

## Request and response

The current [`Request`](/api/request.md) and [`Response`](/api/response.md) objects are provided by the `req` and `res` providers, respectively.

::: tip
This makes the declaration of the `req` and `res` parameters in [HTTP views](/guides/http/views.md) entirely optional. If you don't need them, don't consume them. :+1:
:::

::: warning
These providers are only defined within the context of an **HTTP view**. Using `req` or `res` in a [WebSocket](/guides/websockets/) view has undefined behavior.
:::
