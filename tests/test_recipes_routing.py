import pytest

from bocadillo import App, Recipe, Redirect


def test_if_prefix_not_given_then_routes_mounted_at_slash_name(app, client):
    numbers = Recipe("numbers")

    @numbers.route("/real")
    async def real(req, res):
        pass

    app.recipe(numbers)
    assert client.get("/numbers/real").status_code == 200


def test_if_prefix_then_routes_mounted_at_prefix(app, client):
    numbers = Recipe("numbers", prefix="/numbers-yo")

    @numbers.route("/real")
    async def real(req, res):
        pass

    app.recipe(numbers)
    assert client.get("/numbers-yo/real").status_code == 200


def test_if_prefix_does_not_start_with_slash_then_error_raised():
    with pytest.raises(AssertionError):
        Recipe("numbers", prefix="numbers-yo")


def test_redirect(app: App, client):
    numbers = Recipe("numbers")

    @numbers.route("/R")
    async def R(req, res):
        raise Redirect("/numbers/real")

    @numbers.route("/real")
    async def real(req, res):
        res.text = "inf"

    app.recipe(numbers)

    response = client.get("/numbers/R")
    assert response.status_code == 200
    assert response.text == "inf"
