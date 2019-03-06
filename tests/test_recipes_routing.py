import pytest

from bocadillo import App, Recipe


def test_if_prefix_not_given_then_routes_mounted_at_slash_name(app: App):
    numbers = Recipe("numbers")

    @numbers.route("/real")
    async def real(req, res):
        pass

    app.recipe(numbers)

    assert app.url_for("numbers:real") == "/numbers/real"


def test_if_prefix_then_routes_mounted_at_prefix(app: App):
    numbers = Recipe("numbers", prefix="/numbers-yo")

    @numbers.route("/real")
    async def real(req, res):
        pass

    app.recipe(numbers)

    assert app.url_for("numbers:real") == "/numbers-yo/real"


def test_if_prefix_does_not_start_with_slash_then_error_raised():
    with pytest.raises(AssertionError):
        Recipe("numbers", prefix="numbers-yo")


def test_url_for():
    numbers = Recipe("numbers")

    @numbers.route("/real")
    async def real(req, res):
        pass

    assert numbers.url_for("numbers:real") == "/numbers/real"


def test_redirect(app: App, client):
    numbers = Recipe("numbers")

    @numbers.route("/R")
    async def R(req, res):
        numbers.redirect(name="numbers:real")

    @numbers.route("/real")
    async def real(req, res):
        res.text = "inf"

    app.recipe(numbers)

    response = client.get("/numbers/R")
    assert response.status_code == 200
    assert response.text == "inf"
