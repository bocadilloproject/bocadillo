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

1. Open up a terminal, and create an empty directory somewhere on your computer, then `cd` to it:

```bash
mkdir ~/dev/bocadillo-chatbot
cd ~/dev/bocadillo-chatbot
```

2. [Install Bocadillo](/getting-started/installation.md) and ChatterBot. We're using [pipenv] to install dependencies, but you can also use plain ol' `pip`, or enter the future with [piploc](https://github.com/cs01/pythonloc).

[pipenv]: https://pipenv.readthedocs.io

```bash
pipenv install bocadillo chatterbot pytz
```

3. Create an empty `app.py` script. This is where we'll create the application later on:

```bash
touch app.py
```

We should now have the following directory structure:

```bash
$ tree
.
├── Pipfile
├── Pipfile.lock
└── app.py
```

## Bootstrapping the application

Now, let's write the app skeleton in `app.py`:

```python
# app.py
from bocadillo import App

app = App()
```

All we have to do to start the server is give the `app` object to [uvicorn]:

[uvicorn]: https://www.uvicorn.org

```bash
uvicorn app:app
```

If you go to [http://localhost:8000](http://localhost:8000) and get a `404 Not Found` response, you're all good! Enter `Ctrl+C` in your terminal to stop the server.

## Writing the WebSocket endpoint

We're now ready to get to the meat of it! The first thing we'll build is the WebSocket endpoint.

If you're not familiar with WebSocket, don't worry — here's a 10-word summary: it allows a server and a client to exchange messages in a bidirectional way. It's good old sockets reinvented for the web.

Due to their **bidirectional nature**, they're very suitable for the kind of application we're building here — some sort of _conversation_ between a client and a server (i.e. our chatbot).

If you're interested in learning more about WebSockets in Python, I strongly recommend this talk: [A beginner's guide to WebSockets](https://www.youtube.com/watch?v=PjiXkJ6P9pQ).

Alright, so we're not going to plug the chatbot in just yet. Instead, let's make the server send back any message it receives — a behavior also known as an "echo" endpoint.

Add the following between the `app` object declaration in `app.py`:

```python
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

Create a `client.py` file and paste the following code there. It connects to the WebSocket endpoint and runs a simple REPL:

```python
# client.py
import asyncio
from contextlib import suppress
import websockets

async def client(url: str):
    async with websockets.connect(url) as websocket:
        while True:
            message = input("> ")
            await websocket.send(message)
            response = await websocket.recv()
            print(response)

with suppress(KeyboardInterrupt):
    asyncio.run(client("ws://localhost:8000/conversation"))
```

Run the server-side application with `uvicorn app:app` and, in a separate terminal, start the `client.py` script. You should be greeted with a `>` prompt. If so, start chattin'!

```
$ python client.py
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

Go ahead and create a chatbot.py file, and add Diego in there:

```python
# chatbot.py
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

diego = ChatBot("Diego")

trainer = ChatterBotCorpusTrainer(diego)
trainer.train(
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations"
)
```

(ChatterBot's chatbots are quite dumb out of the box, so the code above trains Diego on an English corpus to make him a bit smarter.)

At this point, you can try out the chatbot in a Python interpreter:

```python
$ python
>>> from chatbot import diego  # Be patient — this may take a few seconds to load!
>>> diego.get_response("Hi, there!")
<Statement text:There should be one-- and preferably only one --obvious way to do it.>
```

(Hmm. Interesting response! 🐍)

Let's now plug Diego into the WebSocket endpoint: each time we receive a new `message`, we'll give it to Diego and send his response back.

```python
# app.py
from chatbot import diego

...

@app.websocket_route("/conversation")
async def converse(ws):
    async for message in ws:
        response = diego.get_response(message)
        await ws.send(str(response))
```

If you run the [server/client setup](#trying-out-the-websocket-endpoint) from earlier, you can now see that Diego converses with us over the WebSocket!

```
$ python client.py
> Hi there!
I am a chat bot. I am the original chat bot. Did you know that I am incapable of error?
> Where are you?
I am on the Internet.
>
```

Looks like Diego is a jokester. 😉

## Refactoring the chatbot as a provider

Clients are now able to chat with Diego over a WebSocket connection. That's great!

However, there are a few non-functional issues with our current setup:

- Loading Diego is quite expensive: it takes about ten seconds on a regular laptop.
- Because of the `import` at the top of the script, we'd load Diego every time we import the `app` module. Not great!
- Diego is injected as a global dependency into the WebSocket endpoint: we can't swap it with another implementation (especially useful during tests), and it's not immediately clear that the endpoint depends on it at first sight.

If you think about it, Diego is a **resource** — ideally, it should only be made available to the WebSocket endpoint at the time of processing a connection request.

So, there must be a better way… and there is: [providers]. ✨

Providers are a unique feature of Bocadillo. They were inspired by [pytest fixtures] and offer an elegant, modular and flexible way to **manage and inject resources into web views**.

[pytest fixtures]: https://docs.pytest.org/en/latest/fixture.html

Let's use them to fix the code, shall we?

First, let's move Diego to a `providerconf.py` script:

```python
# providerconf.py
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from bocadillo import provider

@provider(scope="app")
def diego():
    diego = ChatBot("Diego")

    trainer = ChatterBotCorpusTrainer(diego)
    trainer.train(
        "chatterbot.corpus.english.greetings",
        "chatterbot.corpus.english.conversations",
    )

    return diego
```

The code above declares a `diego` provider which we can now **inject** into the WebSocket view. All we have to do is declare it as a **parameter** to the view.

Let's do just that by updating the `app.py` script. Here, you get it in full:

```python
from bocadillo import App

app = App()

@app.websocket_route("/conversation")
async def converse(ws, diego):  # <-- 👋, Diego!
    async for message in ws:
        response = diego.get_response(message)
        await ws.send(str(response))
```

No imports required — Diego will _automagically_ get injected in the WebSocket view when processing the WebSocket connection request. ✨

Alright, ready to try things out?

1. Run the server using [uvicorn]. You should see additional logs corresponding to Bocadillo setting up Diego on startup:

```bash
$ uvicorn app:app
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

2. Run the `client.py` script, and start chatting! You shouldn't see any difference from before. In particular, Diego responds just as fast.

```
$ python client.py
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
# providerconf.py
from bocadillo import provider

...

@provider(scope="app")
def clients():
    return set()
```

2. Add another provider which returns a context manager that takes care of registering the `ws` connection to the set of clients. FYI, this is an example of a [factory provider][factory providers], but you don't really need to understand the whole code at this point.

[factory providers]: /guides/injection/factory.md

```python
# providerconf.py
from contextlib import contextmanager
from bocadillo import provider

...

@provider
def save_client(clients):
    @contextmanager
    def _register(ws):
        clients.add(ws)
        try:
            yield ws
        finally:
            clients.remove(ws)

    return _register
```

3. In the WebSocket view, use the new `save_client` provider to register the WebSocket client:

```python
# app.py

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

## Exposing client count via a REST endpoint

As a final feature, let's step aside from WebSocket for a moment and go back to the good old HTTP protocol. We'll create a simple REST endpoint to view the number of currently connected clients.

Go back to `app.py` and add the following code:

```python
# app.py

...

@app.route("/client-count")
async def client_count(req, res, clients):
    res.json = {"count": len(clients)}
```

If you went through the [quickstart] example, hopefully this code shouldn't come as a surprise. All we do here is send the number of `clients` (obtained from the `clients` provider) in a JSON response.

Go ahead! Run `uvicorn app:app` and a few `python client.py` instances, and check out how many clients are connected by opening [http://localhost:8000/client-count](http://localhost:8000/client-count) in a web browser. Press `Ctrl+C` for one of the clients, and see the client count go down!

Did it work? Congrats! ✨

## Testing

We're mostly done in terms of the features we wanted to cover together. We have some ideas you can explore as exercises, of course, but before getting to that let's write some tests.

One of Bocadillo's design principles is to make it easy to write high-quality applications. As such, Bocadillo has all the tools built-in to write tests for this chatbot server.

You can write those with your favorite test framework. We'll choose [pytest] for the purpose of this tutorial. Let's install it first:

```bash
pipenv install --dev pytest
```

Now, let's setup our testing environment. We'll write a [pytest fixture][pytest fixtures] that sets up a test client. It exposes a Requests-like API as well as helpers to test WebSocket endpoints. Besides, we don't actually need to test the chatbot here, so we'll override the `diego` provider with an "echo" mock — this will have the nice side effect of greatly speeding up the tests.

So, go ahead and create a `conftest.py` script and place the following in there:

```python
# conftest.py
import pytest
from bocadillo import provider
from bocadillo.testing import create_client

from app import app

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

Now is the time to write some tests! Create a `test_app.py` file at the project root directory:

```bash
touch test_app.py
```

First, let's test that we can connect to the WebSocket endpoint, and that we get a response from Diego if we send a message:

```python
# test_app.py

def test_connect_and_converse(client):
    with client.websocket_connect("/conversation") as ws:
        ws.send_text("Hello!")
        assert ws.receive_text() == "Hello!"
```

Now, let's test the incrementation of the client counter when clients connect to the WebSocket endpoint:

```python
# test_app.py
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

- Setup a Bocadillo project
- Write a WebSocket endpoint.
- Write an HTTP endpoint.
- Use providers to decouple resources and their consumers.
- Test WebSocket and HTTP endpoints.

The complete code for this tutorial is available on our GitHub repo: <repo-page to="docs/getting-started/tutorial" branch="docs" text="get the code"/>. All in all, the server and `providerconf.py` only add up to about 60 lines of code — pretty good bang for the buck!

## Next steps

Obviously, we've only scratched the surface of what you can do with Bocadillo. The goal of this tutorial was to take you through the steps of building a _Minimum Meaningful Application_.

You can iterate upon this chatbot server we've built together very easily. We'd be happy to see what you come up with!

Want to challenge yourself? Here are a few ideas:

- Add a home page rendered with [templates]. The web browser should connect to the chatbot server via a JavaScript program. You'll probably also need to serve [static files] to achieve this.
- [Train Diego](https://chatterbot.readthedocs.io/en/stable/training.html) to answers questions like "How many people are you talking to currently?"
- Currently, all clients talk to the same instance of Diego. Yet, it would be nice if each client had their own Diego to ensure a bespoke conversation. You may want to investigate [cookie-based sessions] and [factory providers] to implement this behavior.

[cookie-based sessions]: /guides/agnostic/sessions.md
[templates]: /guides/agnostic/templates.md
[static files]: /guides/http/static-files.md

To learn more about HTTP views, WebSocket views, providers, and much more, you can continue to the [Guides](/guides/) section.

Have fun working with Bocadillo! 🥪
