from bocadillo import App


def test_attachment(app: App, client):
    @app.route("/")
    async def index(req, res):
        res.text = "hello.text"
        res.attachment = "hello.txt"

    response = client.get("/")
    assert response.status_code == 200
    assert (
        response.headers["content-disposition"]
        == "attachment; filename='hello.txt'"
    )
