# Events

Bocadillo implements the [ASGI Lifespan protocol](https://asgi.readthedocs.io/en/latest/specs/lifespan.html), which allows you to hook into the server's initialization and teardown via events and event handlers.

Events are especially helpful when you need to setup resources on server startup and make sure you clean them up when the server stops.

## Registering events

Event handlers are callbacks, i.e. functions with the signature `() -> None`.

They can be registered using the `@api.on()` decorator:

```python
@api.on("startup")
async def setup():
    # Perform setup when server boots
    pass

@api.on("shutdown")
async def cleanup():
    # Perform cleanup when server shuts down
    pass
```

A non-decorator syntax is also available:

```python
async def setup():
    pass

api.on("shutdown", setup)
```

Only the `"startup"` and `"shutdown"` events are supported.

::: tip
Event handlers can also be regular, non-async functions.
:::
