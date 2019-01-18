from asyncio import sleep
from multiprocessing import Value

import pytest
import requests

from bocadillo import API
from bocadillo.request import ClientDisconnect

from .utils import stops_incrementing, Server


def test_if_nothing_set_then_response_is_empty(api: API):
    @api.route("/")
    async def index(req, res):
        pass

    response = api.client.get("/")
    assert not response.text


def test_if_status_code_is_no_content_then_no_content_type_set(api: API):
    @api.route("/")
    async def index(req, res):
        res.status_code = 204
        pass

    response = api.client.get("/")
    assert response.status_code == 204
    assert not response.text
    assert response.headers.get("content-type") is None


def test_content_type_defaults_to_plaintext(api: API):
    @api.route("/")
    async def index(req, res):
        res.content = "Something magical"
        # make sure no content-type is set before leaving the view
        res.headers.pop("Content-Type", None)
        pass

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "text/plain"


def test_if_text_set_then_response_is_plain_text(api: API):
    @api.route("/")
    async def index(req, res):
        res.text = "foo"
        pass

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "text/plain"
    assert response.text == "foo"


def test_if_media_set_then_response_is_json(api: API):
    @api.route("/")
    async def index(req, res):
        res.media = {"foo": "bar"}

    response = api.client.get("/")
    assert response.json() == {"foo": "bar"}


def test_if_html_set_then_response_is_html(api: API):
    @api.route("/")
    async def index(req, res):
        res.html = "<h1>Foo</h1>"

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "text/html"
    assert response.text == "<h1>Foo</h1>"


def test_last_response_setter_called_has_priority(api: API):
    @api.route("/")
    async def index(req, res):
        res.media = {"foo": "bar"}
        res.text = "foo"
        pass

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "text/plain"
    assert response.text == "foo"

    @api.route("/")
    async def index(req, res):
        res.text = "foo"
        res.media = {"foo": "bar"}
        pass

    response = api.client.get("/")
    assert response.headers["Content-Type"] == "application/json"
    assert response.json() == {"foo": "bar"}


def test_chunked_response(api: API):
    @api.route("/")
    async def index(req, res):
        res.chunked = True

    r = api.client.get("/")
    assert r.headers["transfer-encoding"] == "chunked"


def test_stream_response(api: API):
    background_called = False

    @api.route("/{word}")
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

    r = api.client.get("/hello")
    assert r.text == "hello"
    assert r.headers["x-foo"] == "foo"
    assert r.status_code == 202
    assert background_called
    # streaming does not send the response in chunks
    assert "transfer-encoding" not in r.headers


def test_stream_func_must_be_async_generator_function(api: API):
    @api.route("/")
    async def index(req, res):
        with pytest.raises(AssertionError):
            # Regular function
            @res.stream
            def foo():
                pass

        with pytest.raises(AssertionError):
            # Coroutine function
            @res.stream
            async def bar():
                pass

        with pytest.raises(AssertionError):
            # Regular generator
            @res.stream
            def duh():
                yield "nope"


def test_stop_on_client_disconnect(api: API):
    sent = Value("i", 0)
    caught = Value("i", 0)

    @api.route("/inf")
    async def infinity(req, res):
        @res.stream
        async def stream():
            nonlocal sent, caught
            try:
                while True:
                    yield "∞"
                    sent.value += 1
            except ClientDisconnect:
                caught.value = 1

    with Server(api) as server:
        r = requests.get(f"{server.base_url}/inf", stream=True)
        assert r.status_code == 200
        assert stops_incrementing(counter=sent, response=r)
        assert caught.value
