from bocadillo import App


def test_parameter_is_passed_as_argument(app: App, client):
    @app.route("/greet/{person}")
    async def greet(req, res, person: str):
        res.text = person

    response = client.get("/greet/John")
    assert response.status_code == 200
    assert response.text == "John"


def test_if_route_expects_int_but_int_not_given_then_404(app: App, client):
    @app.route("/add/{x:d}/{y:d}")
    async def add(req, res, x, y):
        res.text = str(x + y)

    response = client.get("/add/1/foo")
    assert response.status_code == 404
