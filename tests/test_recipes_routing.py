import pytest

from bocadillo import API, Recipe


def test_if_prefix_not_given_then_routes_mounted_at_slash_name(api: API):
    numbers = Recipe("numbers")

    @numbers.route("/real")
    async def real(req, res):
        pass

    api.recipe(numbers)

    assert api.url_for("numbers:real") == "/numbers/real"


def test_if_prefix_then_routes_mounted_at_prefix(api: API):
    numbers = Recipe("numbers", prefix="/numbers-yo")

    @numbers.route("/real")
    async def real(req, res):
        pass

    api.recipe(numbers)

    assert api.url_for("numbers:real") == "/numbers-yo/real"


def test_if_prefix_does_not_start_with_slash_then_error_raised():
    with pytest.raises(AssertionError):
        Recipe("numbers", prefix="numbers-yo")
