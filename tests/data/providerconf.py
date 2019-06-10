from bocadillo import provider


@provider
async def hello_format():
    return "Hello, {who}!"


@provider
async def hello(hello_format) -> str:
    return hello_format.format(who="providers")


@provider(name="foo")
async def provide_foo():
    return "foo"


@provider(scope="app")
async def clients():
    return set()


CALLED = False


@provider
async def spy():
    return {"called": CALLED}


@provider
async def set_called():
    global CALLED
    CALLED = True
