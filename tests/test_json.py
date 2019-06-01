from bocadillo import App


def test_json_response(app: App, client):
    data = {"message": "hello"}

    @app.route("/")
    async def index(req, res):
        res.json = data

    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == data
