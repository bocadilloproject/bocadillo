from bocadillo import API


def test_parameter_is_passed_as_argument(api: API):
    @api.route("/greet/{person}")
    async def greet(req, res, person: str):
        res.text = person

    response = api.client.get("/greet/John")
    assert response.status_code == 200
    assert response.text == "John"


def test_if_route_expects_int_but_int_not_given_then_404(api: API):
    @api.route("/add/{x:d}/{y:d}")
    async def add(req, res, x, y):
        res.text = str(x + y)

    response = api.client.get("/add/1/foo")
    assert response.status_code == 404
