# WebSockets by example: real-time chat room

This example application demonstrates building a rudimentary chat room app with Bocadillo WebSockets.

The server exposes:

- A WebSocket endpoint, which keeps track of connected clients, sends the in-memory history of messages to new clients and broadcasts new messages. Clients and messages are stored using [providers](/guides/injection/).
- A home page rendered with an HTML template. The page contains a vanilla JavaScript script which creates a WebSocket client and updates the DOM when new messages are received.

Usage:

- Execute the `app.py` script: `python app.py`.
- Then, open a web browser at [http://localhost:8000](http://localhost:8000) to start chatting!

## Provider configuration

<<<@/docs/guides/websockets/example/providerconf.py

## Application script

<<<@/docs/guides/websockets/example/app.py

## HTML template

<<<@/docs/guides/websockets/example/templates/index.html
