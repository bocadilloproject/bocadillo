from asyncio import sleep
from multiprocessing import Value
from time import sleep as sync_sleep

import pytest
import requests

from bocadillo import App, ClientDisconnect, LiveServer

from .utils import stops_incrementing


def test_stream_response(app: App, client):
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

    r = client.get("/hello")
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
            # Regular function (non-generator)
            @res.stream
            def foo():
                pass

        with pytest.raises(AssertionError):
            # Coroutine function (non-generator)
            @res.stream
            async def bar():
                pass

        with pytest.raises(AssertionError):
            # Regular generator
            @res.stream
            def baz():
                yield "nope"


def test_stop_on_client_disconnect(app: App):
    sent = Value("i", 0)

    @app.route("/inf")
    async def infinity(req, res):
        @res.stream
        async def stream():
            nonlocal sent
            while True:
                yield "∞"
                sent.value += 1

    with LiveServer(app) as server:
        r = requests.get(server.url("/inf"), stream=True)
        assert r.status_code == 200
        assert stops_incrementing(counter=sent, response=r)


def test_raise_on_disconnect(app: App):
    caught = Value("i", 0)

    @app.route("/inf")
    async def infinity(req, res):
        @res.stream(raise_on_disconnect=True)
        async def stream():
            nonlocal caught
            try:
                while True:
                    yield "∞"
            except ClientDisconnect:
                caught.value = 1

    with LiveServer(app) as server:
        r = requests.get(server.url("/inf"), stream=True)
        assert r.status_code == 200
        r.close()
        sync_sleep(0.1)
        assert caught.value
