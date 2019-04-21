# Tutorial

You [installed Bocadillo](./installation.md) and went through the [quickstart] example, but you'd like a guided tour on how to work with Bocadillo? Look no further!

[quickstart]: ./quickstart.md

In this step-by-step tutorial, we'll try and build a **chatbot server**! What could possibly go wrong?

We'll go through many aspects of building apps with Bocadillo, including:

- Using the built-in [WebSocket] support to handle multiple connections in real-time.
- Creating REST endpoints using [HTTP routing](/guides/http/routing.md) and [views](/guides/http/views.md).
- Using [providers] to inject reusable resources into views.
- [Testing] an application using [pytest].

[websocket]: /guides/websockets/
[providers]: /guides/injection/
[testing]: /guides/architecture/testing.md
[pytest]: https://docs.pytest.org

We'll use the [ChatterBot] library to build **Diego**, a friendly conversational agent. Don't worry, this won't require _any_ background in data science nor chatbot technology!

[chatterbot]: https://github.com/gunthercox/ChatterBot

Sounds exciting? Let's dive in! 🙌

## Setting up the project

First things first: let's set up our project:

1. Open up a terminal, and go to your favorite development directory. For example

```bash
cd ~/dev
```

2. Install the [Bocadillo CLI] globally:

[bocadillo cli]: https://github.com/bocadilloproject/bocadillo-cli

```bash
pip install bocadillo-cli
```

3. Use the CLI to generate a new project called `chatbot`:

```bash
bocadillo create chatbot
```

4. Run `cd chatbot`, and you should have the following directory structure:

```
$ tree
.
├── README.md
├── chatbot
│   ├── __init__.py
│   ├── app.py
│   ├── asgi.py
│   ├── providerconf.py
│   └── settings.py
└── requirements.txt
```

4. Edit `requirements.txt` to add Chatterbot there:

```txt
bocadillo >= 0.14
chatterbot
pytz  # Required by Chatterbot
```

5. Install dependencies. We're just using pip and a virtualenv here, but you can use any other dependency management solution:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Serving the application

Once this is all done, let's try and serve the app before we go any further. Run the following command:

```bash
uvicorn chatbot.asgi:app
```

If you go to [http://localhost:8000](http://localhost:8000) and get a `404 Not Found` response, you're all good! Enter `Ctrl+C` in your terminal to stop the server.

## Writing the WebSocket endpoint

We're now ready to get to the meat of it! The first thing we'll build is the WebSocket endpoint.

If you're not familiar with WebSocket, don't worry — here's a 10-word summary: it allows a server and a client to exchange messages in a bidirectional way. It's good old sockets reinvented for the web.

Due to their **bidirectional nature**, they're very suitable for the kind of application we're building here — some sort of _conversation_ between a client and a server (i.e. our chatbot).

If you're interested in learning more about WebSockets in Python, I strongly recommend this talk: [A beginner's guide to WebSockets](https://www.youtube.com/watch?v=PjiXkJ6P9pQ).

Alright, so we're not going to plug the chatbot in just yet. Instead, let's make the server send back any message it receives — a behavior also known as an "echo" endpoint.

Add the following at the end of `app.py`:

```python
# chatbot/app.py

...

@app.websocket_route("/conversation")
async def converse(ws):
    async for message in ws:
        await ws.send(message)
```

A few minimal explanations here, for the curious:

- This defines a WebSocket endpoint accessible at the `ws://localhost:8000/conversation` location.
- The `async for message in ws:` line iterates over messages received over the WebSocket.
- Lastly, `await ws.send(message)` sends the received `message` as-is back to the client.

## Trying out the WebSocket endpoint

How about we try this out by creating a WebSocket client? Fear not — we don't need to write any JavaScript. We'll stick to Python and use the [websockets] library, which comes installed with Bocadillo.

[websockets]: https://websockets.readthedocs.io

Create a `client.py` file in the project root directory, and paste the following code there. It connects to the WebSocket endpoint and runs a simple REPL:

<<<@/docs/getting-started/tutorial/client.py

Serve the app again and, in a separate terminal, run `$ python client.py`. You should be greeted with a `>` prompt. If so, start chattin'!

```
> Hi!
Hi!
> Is there anyone here?
Is there anyone here?
>
```

Pretty cool, isn't it? 🤓

Type `Ctrl+C` to exit the session and close the WebSocket connection.

## Hello, Diego!

Now that we're able to make the server and a client communicate, how about we replace the echo implementation with an actual, intelligent and friendly chatbot?

This is where [ChatterBot] comes in! We'll create a chatbot rightfully named **Diego** — a chatbot speaking the asynchronous salsa. 🕺

Go ahead and create a `bot.py` file, and add Diego in there:

<<<@/docs/getting-started/tutorial/chatbot/bot.py

(ChatterBot's chatbots are quite dumb out of the box, so the code above trains Diego on an English corpus to make him a bit smarter.)

At this point, you can try out the chatbot in a Python interpreter:

```python
$ python
>>> from chatbot.bot import diego  # Be patient — this may take a few seconds to load!
>>> diego.get_response("Hi, there!")
<Statement text:There should be one-- and preferably only one --obvious way to do it.>
```

(Hmm. Interesting response! 🐍)

Let's now plug Diego into the WebSocket endpoint: each time we receive a new `message`, we'll give it to Diego and send his response back.

```python
# chatbot/app.py
from .bot import diego

...

@app.websocket_route("/conversation")
async def converse(ws):
    async for message in ws:
        response = diego.get_response(message)
        await ws.send(str(response))
```

If you run the [server/client setup](#trying-out-the-websocket-endpoint) from earlier, you can now see that Diego converses with us over the WebSocket!

```
> Hi there!
I am a chat bot. I am the original chat bot. Did you know that I am incapable of error?
> Where are you?
I am on the Internet.
>
```

Looks like Diego is a jokester. 😉

## Refactoring the chatbot as a provider

Clients are now able to chat with Diego over a WebSocket connection. That's great!

However, there are a few non-functional issues with our current setup. If you think about it, Diego is a **resource** — ideally, it should only be made available to the WebSocket endpoint at the time of processing a connection request. Instead, we load it as soon as the `app` module gets imported. Plus, it is injected as a global dependency which makes the code hard to test and less readable.

So, there must be a better way… and there is: [providers]. ✨

Providers are quite unique to Bocadillo. They were inspired by [pytest fixtures] and offer an elegant, modular and flexible way to **manage and inject resources into web views**.

[pytest fixtures]: https://docs.pytest.org/en/latest/fixture.html

Let's use them to fix the code, shall we?

Open the `providerconf.py` module that was generated by the CLI, and add the following code:

```python
# chatbot/providerconf.py
from bocadillo import provider

@provider(scope="app")
def diego():
    from .bot import diego

    return diego
```

This code declares a `diego` provider which lazily loads the chatbot on app startup (hence `scope="app"`).

We can now **inject** Diego into the WebSocket view. All we have to do is declare it as a **parameter** to the view. Let's do just that by updating the `app.py` script, which is listed here in full:

```python
# chatbot/app.py
from bocadillo import App, discover_providers

app = App()
discover_providers("chatbot.providerconf")


@app.websocket_route("/conversation")
async def converse(ws, diego):  # <-- 👋, Diego!
    async for message in ws:
        response = diego.get_response(message)
        await ws.send(str(response))
```

No imports required — Diego will _automagically_ get injected in the WebSocket view when processing the WebSocket connection request. ✨

Ready to try things out?

1. Run the server. You should see additional logs corresponding to Bocadillo setting up Diego on startup:

```
$ uvicorn chatbot.asgi:app
INFO: Started server process [29843]
INFO: Waiting for application startup.
[nltk_data] Downloading package averaged_perceptron_tagger to
[nltk_data]     /Users/Florimond/nltk_data...
[nltk_data]   Package averaged_perceptron_tagger is already up-to-
[nltk_data]       date!
[nltk_data] Downloading package punkt to /Users/Florimond/nltk_data...
[nltk_data]   Package punkt is already up-to-date!
[nltk_data] Downloading package stopwords to
[nltk_data]     /Users/Florimond/nltk_data...
[nltk_data]   Package stopwords is already up-to-date!
Training greetings.yml: [####################] 100%
Training conversations.yml: [####################] 100%
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

2. Run the `client.py` script again, and start chatting! You shouldn't see any difference from before. In particular, Diego responds just as fast.

```
> Hello!
Hi
> I would like to order a sandwich
Yes it is.
>
```

There you go! Beautiful, modular and flexible [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection) with Bocadillo providers.

## Keeping track of clients

Let's go one step further. True, we have quite elegantly implemented conversation with a chatbot over WebSocket. Now, how about we keep track of how many clients are currently talking to the chatbot?

If you were wondering, the answer is yes — we can implement this with providers too!

1. Add a `clients` provider to `providerconf.py`:

```python
# chatbot/providerconf.py
from bocadillo import provider

...

@provider(scope="app")
def clients():
    return set()
```

2. Add another provider which returns a context manager that takes care of adding the `ws` connection to the set of clients. FYI, this is an example of a [factory provider][factory providers], but you don't really need to understand the whole code at this point.

[factory providers]: /guides/injection/factory.md

```python
# chatbot/providerconf.py
from contextlib import contextmanager
from bocadillo import provider

...

@provider
def save_client(clients):
    @contextmanager
    def _save(ws):
        clients.add(ws)
        try:
            yield ws
        finally:
            clients.remove(ws)

    return _save
```

3. In the WebSocket view, use the new `save_client` provider to register the WebSocket client:

```python
# chatbot/app.py

...

@app.websocket_route("/conversation")
async def converse(ws, diego, save_client):
    with save_client(ws):
        async for message in ws:
            response = diego.get_response(message)
            await ws.send(str(response))
```

That's it! While the client is chatting with Diego, it will be present in the set of `clients`.

How about we do something with this information?

## Exposing clients count via a REST endpoint

As a final feature, let's step aside from WebSocket for a moment and go back to the good old HTTP protocol. We'll create a simple REST endpoint to view the number of currently connected clients.

Go back to `app.py` and add the following code:

```python
# chatbot/app.py

...

@app.route("/client-count")
async def client_count(req, res, clients):
    res.json = {"count": len(clients)}
```

Hopefully this code shouldn't come as a surprise. All we do here is send the number of `clients` (obtained from the `clients` provider) in a JSON response.

Go ahead! Run `uvicorn chatbot.asgi:app`, and a few `python client.py` instances, and check out how many clients are connected by opening [http://localhost:8000/client-count](http://localhost:8000/client-count) in a web browser. Press `Ctrl+C` for one of the clients, and see the client count go down!

Did it work? Congrats! ✨

## Testing

We're mostly done in terms of the features we wanted to cover together. We have some ideas you can explore as exercises, of course, but before getting to that let's write some tests.

One of Bocadillo's design principles is to make it easy to write high-quality applications. As such, Bocadillo has all the tools built-in to write tests for this chatbot server.

You can write those with your favorite test framework. We'll choose [pytest] for the purpose of this tutorial. Let's install it first:

```bash
pip install pytest
```

Next, create a tests package:

```bash
mkdir tests
```

We can now setup our testing environment:

- We'll write a [pytest fixture][pytest fixtures] that sets up a test client. The test client exposes a Requests-like API as well as helpers to test WebSocket endpoints.
- We don't actually need to test the chatbot here, so we'll override the `diego` provider with an "echo" mock — this will have the nice side effect of greatly speeding up the tests.

Go ahead and create a `conftest.py` script and place the following in there:

```python
# tests/conftest.py
import pytest
from bocadillo import provider, create_client

from chatbot.asgi import app

@provider
def diego():
    class EchoDiego:
        def get_response(self, query):
            return query

    return EchoDiego()

@pytest.fixture
def client():
    return create_client(app)
```

Now is the time to write some tests! Create a `test_app.py` file in the tests package:

```bash
touch tests/test_app.py
```

First, let's test that we can connect to the WebSocket endpoint, and that we get a response from Diego if we send a message:

```python
# tests/test_app.py

def test_connect_and_converse(client):
    with client.websocket_connect("/conversation") as ws:
        ws.send_text("Hello!")
        assert ws.receive_text() == "Hello!"
```

Now, let's test the incrementation of the client counter when clients connect to the WebSocket endpoint:

```python
# tests/test_app.py
...

def test_client_count(client):
    assert client.get("/client-count").json() == {"count": 0}

    with client.websocket_connect("/conversation"):
        assert client.get("/client-count").json() == {"count": 1}

    assert client.get("/client-count").json() == {"count": 0}
```

Run these tests using:

```bash
pytest
```

And, well, guess what?

```bash
==================== test session starts =====================
platform darwin -- Python 3.7.2, pytest-4.3.1, py-1.8.0, pluggy-0.9.0
rootdir: ..., inifile: pytest.ini
collected 2 items

test_app.py ..                                         [100%]

================== 2 passed in 0.08 seconds ==================
```

Tests pass! ✅🎉

## Wrapping up

If you've made it so far — congratulations! You've just built a **chatbot server** powered by WebSocket, [ChatterBot] and Bocadillo.

Together, we've seen how to:

- Setup a project using the [Bocadillo CLI] and edit its contents.
- Write WebSocket and HTTP endpoints.
- Use providers to decouple resources from their consumers.
- Test WebSocket and HTTP endpoints using pytest and Bocadillo's testing helpers.

The complete code for this tutorial is available on our GitHub repo: [get the code](https://github.com/bocadilloproject/bocadillo/blob/master/docs/getting-started/tutorial/).

## Next steps

Obviously, we've only scratched the surface of what you can do with Bocadillo. The goal of this tutorial was to take you through the steps of building your First Meaningful Application.

You can iterate upon this chatbot server we've built together very easily. We'd be happy to see what you come up with!

Want to challenge yourself? Here are a few ideas:

- Add a home page rendered with [templates]. The web browser should connect to the chatbot server via a JavaScript program. You'll probably also need to serve [static files] to achieve this.
- [Train Diego](https://chatterbot.readthedocs.io/en/stable/training.html) to answers questions like "How many people are you talking to currently?"
- Currently, all clients talk to the same instance of Diego. Yet, it would be nice if each client had their own Diego to ensure a bespoke conversation. You may want to investigate [cookie-based sessions] and [factory providers] to implement this behavior.

[cookie-based sessions]: /guides/http/sessions.md
[templates]: /guides/agnostic/templates.md
[static files]: /guides/http/static-files.md

To learn more about HTTP views, WebSocket views, providers, and much more, you can continue to the [Guides](/guides/) section.

Have fun working with Bocadillo! 🥪
