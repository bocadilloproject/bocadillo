def test_connect_and_converse(client):
    with client.websocket_connect("/conversation") as ws:
        ws.send_text("Hello!")
        assert ws.receive_text() == "Hello!"


def test_client_count(client):
    assert client.get("/client-count").json() == {"count": 0}

    with client.websocket_connect("/conversation"):
        assert client.get("/client-count").json() == {"count": 1}

    assert client.get("/client-count").json() == {"count": 0}
