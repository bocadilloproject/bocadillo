# WebSockets by example: real-time chat room

This example application demonstrates building a rudimentary chat room app with Bocadillo WebSockets.

The server exposes:

- A WebSocket endpoint, which keeps track of connected clients, sends the in-memory history of messages to new clients and broadcasts new messages.
- A home page rendered with an HTML template. The page contains a vanilla JavaScript script which creates a WebSocket client and updates the DOM when new messages are received.

Usage:

- Execute the `api.py` script: `python api.py`.
- Then, open a web browser at [http://localhost:8000](http://localhost:8000) to start chatting!

## Application script

<<<@/docs/topics/websockets/example/api.py

## HTML template

<<<@/docs/topics/websockets/example/templates/index.html
