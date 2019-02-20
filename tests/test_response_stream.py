from asyncio import sleep

import pytest
from bocadillo import App


def test_stream_response(app: App):
    background_called = False

    @app.route("/{word}")
    async def index(req, res, word: str):
        @res.stream
        async def stream_word():
            for character in word:
                yield character
                await sleep(0.001)

        # Other features of res can also be used

        res.headers["x-foo"] = "foo"
        res.status_code = 202

        @res.background
        async def do_later():
            nonlocal background_called
            background_called = True

    r = app.client.get("/hello")
    assert r.text == "hello"
    assert r.headers["x-foo"] == "foo"
    assert r.status_code == 202
    assert background_called
    # streaming does not send the response in chunks
    assert "transfer-encoding" not in r.headers


def test_stream_func_must_be_async_generator_function(app: App):
    @app.route("/")
    async def index(req, res):
        with pytest.raises(AssertionError):
            # Regular function
            @res.stream
            def foo():
                pass

        with pytest.raises(AssertionError):
            # Coroutine function
            @res.stream
            async def foo():
                pass

        with pytest.raises(AssertionError):
            # Regular generator
            @res.stream
            def foo():
                yield "nope"
