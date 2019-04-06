from bocadillo import App


def test_parameter_is_passed_as_keyword_argument(app: App, client):
    @app.route("/greet/{person}")
    async def greet(req, res, *, person: str):
        res.text = person

    response = client.get("/greet/John")
    assert response.status_code == 200
    assert response.text == "John"
