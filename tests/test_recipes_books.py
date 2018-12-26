import pytest

from bocadillo import API, Recipe


@pytest.fixture
def numbers():
    integers = Recipe("integers")

    @integers.route("/{x}")
    class Convert:
        async def get(self, req, res, x):
            res.media = {"value": int(float(x))}

    floats = Recipe("floats")

    @floats.route("/{x}")
    class Convert:
        async def get(self, req, res, x):
            res.media = {"value": float(x)}

    return Recipe.book(integers, floats, prefix="/numbers")


def test_recipe_book(api: API, numbers):
    api.recipe(numbers)

    response = api.client.get("/numbers/integers/3.5")
    assert response.status_code == 200
    assert response.json() == {"value": 3}

    response = api.client.get("/numbers/floats/1")
    assert response.status_code == 200
    assert response.json() == {"value": 1.0}
