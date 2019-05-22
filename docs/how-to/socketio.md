# Build a real-time application with socket.io

If you're interested in using [socket.io][socketio] (a.k.a. SocketIO) to build a real-time web application, Bocadillo got you covered.

In this guide, we'll go through the process of rewriting the [socket.io chat tutorial] with Bocadillo, [python-socketio] and the [socket.io-client] library.

All the code can be found in our [socketio-example repository][socketio-example] on GitHub.

[socketio]: https://socket.io
[python-socketio]: https://python-socketio.readthedocs.io
[socket.io chat tutorial]: https://socket.io/get-started/chat/
[socket.io-client]: https://github.com/socketio/socket.io-client
[socketio-example]: https://github.com/bocadilloproject/socketio-example

## Planning

What are we going to build, exactly?

Well, as described in the [socket.io chat tutorial], we'll need:

1. A backend socket.io server to handle incoming messages and broadcast them to all connected clients. This will be done via [python-socketio].
2. A JavaScript socket.io client to send messages typed by the user, and listen to and display messages from other users. We'll use the [socket.io-client] Node.js package for this purpose.
3. A web application server to serve the HTML page, the socket.io server and any static files we need. **This is where Bocadillo kicks in!**

Let's get down to business, shall we?

## Basic application

First, we'll create the Bocadillo application. [Install Bocadillo](/guide/installation.md) if not done already.

::: warning
Due to `python-engineio` not supporting ASGI3 yet (see [#107](https://github.com/miguelgrinberg/python-engineio/issues/107)), you need to use `bocadillo < 0.15` for the moment.
:::

Then, create the following `app.py` file:

```python
# app.py
from bocadillo import App, configure, Templates

app = App()
configure(app)
templates = Templates()

@app.route("/")
async def index(req, res):
    res.html = await templates.render("index.html")
```

All we're doing here is creating a Bocadillo application with a root endpoint that serves an HTML page, which we're now going to set up. We'll start from the HTML page provided in the [socket.io chat tutorial].

1. First, create a `static` directory in the project root directory, and place the following CSS file there. You can check out the [Static files](/guide/static-files.md) guide to know how Bocadillo will pick that up.

```css
/* static/styles.css */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font: 13px Helvetica, Arial;
}
form {
  background: #000;
  padding: 3px;
  position: fixed;
  bottom: 0;
  width: 100%;
}
form input {
  border: 0;
  padding: 10px;
  width: 90%;
  margin-right: 0.5%;
}
form button {
  width: 9%;
  background: rgb(130, 224, 255);
  border: none;
  padding: 10px;
}
#messages {
  list-style-type: none;
  margin: 0;
  padding: 0;
}
#messages li {
  padding: 5px 10px;
}
#messages li:nth-child(odd) {
  background: #eee;
}
```

2. Next, create a `templates` directory and place the following `index.html` HTML file there. See [Templates](/guide/templates.md) if you need a quick refresher about serving templates in Bocadillo.

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <title>Chat | Bocadillo + socket.io</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" type="text/css" href="/static/styles.css" />
  </head>
  <body>
    <ul id="messages"></ul>
    <form id="form" action="">
      <input id="message" autocomplete="off" /><button>Send</button>
    </form>
  </body>
</html>
```

## Integrating with `python-socketio`

It's now time we integrate [python-socketio] to build the socket.io server.

First, let's install it:

```bash
pip install python-socketio
```

Now, let's update the `app.py` script:

```python{1,8,9}
import socketio
from bocadillo import App, configure, Templates

app = App()
configure(app)
templates = Templates()

sio = socketio.AsyncServer(async_mode="asgi")
app.mount("/sio", socketio.ASGIApp(sio))

...
```

Let's break this code down:

1. We import the `socketio` package made available by `python-socketio`.
2. We [create an `AsyncServer` instance](https://python-socketio.readthedocs.io/en/latest/server.html#creating-a-server-instance). We need to use the `asgi` async mode so that the server can be wrapped as an ASGI application (see [Deployment strategies (python-socketio)](https://python-socketio.readthedocs.io/en/latest/server.html#uvicorn-daphne-and-other-asgi-servers)).
3. We wrap the server in an `ASGIApp`. It implements the ASGI interface, so we can [mount](/api/applications.md#mount) it under the `/sio` URL prefix to have Bocadillo pass it on requests made to `/sio*`.

The rest of `app.py` is unchanged.

That's it! **We've just integrated `python-socketio` within our Bocadillo application**. We're not quite done yet, but we'll only need to work with `python-socketio` from now on.

## Integrating with `socket.io-client`

To build the client, we'll use the [socket.io-client] library. Let's install it:

```bash
npm install --save socket.io-client
```

::: tip
Our approach here is to install the `socket.io` library and use the static JavaScript files distributed with it.

Alternatively, you could retrieve these files from a CDN. See also the [JavaScript client documentation (socket.io)](https://socket.io/docs/#Javascript-Client).
:::

Next, we'll update the `app.py` script to [serve the static files](/guide/static-files.md#extra-static-files-directories) associated to the socket.io client:

```python
# app.py
from bocadillo import App, Templates, static

app = App()
...
app.mount("/socket.io", static("node_modules/socket.io-client/dist"))
```

Finally, let's have the HTML page load the socket.io client by adding an `<src>` tag after the page's `<body>`:

```html
<!-- templates/index.html -->
<!-- ... -->
<body>
  <!-- ... -->
  <script src="/socket.io/socket.io.js"></script>
</body>
```

All set! We can now proceed to build the application-level logic for the chat application.

## Server: receiving and broadcasting messages

We'll start with the server-side application code. For this chat tutorial, all we need to do is listen to `message` events (the name of the event is arbitrary) and **broadcast** the received message to all connected clients.

Remember: we have an `sio` object reprensenting the asynchronous socket.io server. So, we can define an [event handler][event handlers] to handle `message` events, print the received message for debugging, and emit a `response` event to all clients with the message contents:

```python
# app.py
...

@sio.on("message")
async def broadcast(sid, data: str):
    print("message:", data)
    await sio.emit("response", data)

...
```

This code should be self-explanatory. If you're feeling unsure, be sure to check out the [`python-socketio` documentation on event handlers][event handlers].

[event handlers]: https://python-socketio.readthedocs.io/en/latest/server.html#defining-event-handlers

We're basically done with the socket.io server! Let's setup the code to connect to it on the client-side.

## Client: connecting to the socket.io server

We need to add a new script to the HTML page that will connect to the socket.io server using the `socket.io-client` library. This is how it should look like:

```html
<!-- ... --->
<body>
  <!-- ... --->
  <script>
    const socket = io({ path: "/sio/socket.io" });

    socket.on("connect", () => {
      console.log("Connected!");
    });
    socket.on("disconnect", () => {
      console.log("Lost connection to the server.");
    });
  </script>
</body>
```

This code:

- Specifies that the socket.io client should connect to the server at the `/sio/socket.io` path on the same host (here `localhost:8000`). This path corresponds to the prefix under which we mounted the socket.io server (`/sio`) and the default path under which `python-socketio` expects to receive connection requests (`/socket.io`).
- Adds two event handlers to show when socket.io manages to connect, or when it loses connection to the server.

At this point, if you fire up the application using `uvicorn app:app` and connect to `http://localhost:8000`, you should see a `"Connected!"` message popping up in the browser console.

## Client: handling messages

As a final step, we'll write the client-side code to a) send events when submitting the input form, and b) add new items to the list of messages when receiving messages from the server.

Remember that the body of the `index.html` page contains the following snippet:

```html
<ul id="messages"></ul>
<form id="form" action="">
  <input id="message" autocomplete="off" /><button>Send</button>
</form>
```

So, to send a message to the other people in the chat, we need to hook onto the submission of the `form`, and send a `message` event with the contents of the `input` element.

Then, to display messages received from other people, we'll need to add an event handler for the `response` event, and dynamically append `<li>` elements to the list of messages.

You can add the following code to the JavaScript script we previously added:

```js
const formEl = document.getElementById("form");
const messageEl = document.getElementById("message");
const messageList = document.getElementById("messages");

formEl.onsubmit = event => {
  event.preventDefault();
  socket.emit("message", messageEl.value);
  messageEl.value = "";
  return false;
};

socket.on("response", message => {
  console.log("response:", message);
  const li = document.createElement("li");
  li.innerText = message;
  messageList.appendChild(li);
});
```

## Wrapping up

If you've made it so far, congrats! You've just built a real-time chat application with Bocadillo, [python-socketio] and [socket.io-client].

You can find all the code for this guide in our [socketio-example] repository. The full code contains useful comments, context and links, so be sure to check out the repo!
