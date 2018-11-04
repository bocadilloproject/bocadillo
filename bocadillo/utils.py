import inspect


async def _ensure_async(func, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        await func(*args, **kwargs)
    else:
        func(*args, **kwargs)
