# Error handling

## How exceptions are handled

WebSocket routes do not have advanced error handling mechanisms similar to those available for HTTP routes.

The only thing that Bocadillo does is ensuring that the client receives a 1011 (Internal Error) close event if an exception is raised on the server. This is done by catching exceptions raised in the view and closing the WebSocket before re-raising the exception for further server-side processing.

The only exception to this is some specific cases of [client-side connection closures](#handling-client-side-connection-closures).

## Returning errors

In the world of WebSockets, servers and clients notify one another of errors by closing the connection with an appropriate **close code**. This means that the canonical way of returning an error "response" (if there is such a thing) is to `close()` with an appropriate `code` as argument.

Which `code` should you use, then?

For application-level errors, we recommend you use the **4000-4999 range** for custom close codes and provide the appropriate documentation for your clients. This range is indeed reserved for application use by the WebSocket standard. See also the [CloseEvent] reference page which notably lists all available close codes.

However, standard close codes in the **1000-1015 range** may sometimes fit your use case. For these situations, you can refer to the dictionary of close codes available in the [constants] module.

## Handling client-side connection closures

When the client disconnects while we are trying to `receive()` a message, a `WebSocketDisconnect` exception is raised.

This exception will be automatically caught (and silenced) if all the following conditions are met:

- The exception is raised within a WebSocket context (i.e. when using the `async with` syntax).
- The close code is 1000 (Normal Closure) or 1001 (Going Away), both being considered successful closure codes.

In other cases — such as receiving a 1006 (Abnormal Closure close) code — you will need to handle the exception yourself.

::: tip
You can customize which close codes are caught within the WebSocket context by passing a tuple of integers to the `caught_close_codes` parameter of `@api.websocket_route()`. The `all` Python built-in can be passed to catch all close codes. To not catch any close code, pass the empty tuple `()`.
:::

[CloseEvent]: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
[constants]: ../../api/constants.md
