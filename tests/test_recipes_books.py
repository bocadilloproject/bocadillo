import pytest

from bocadillo import App, Recipe


@pytest.fixture
def numbers():
    integers = Recipe("integers")

    @integers.route("/{x}")
    async def convert(req, res, x):
        res.json = {"value": int(float(x))}

    floats = Recipe("floats")

    @floats.route("/{x}")
    async def convert(req, res, x):
        res.json = {"value": float(x)}

    return Recipe.book(integers, floats, prefix="/numbers")


def test_recipe_book(app: App, client, numbers):
    app.recipe(numbers)

    response = client.get("/numbers/integers/3.5")
    assert response.status_code == 200
    assert response.json() == {"value": 3}

    response = client.get("/numbers/floats/1")
    assert response.status_code == 200
    assert response.json() == {"value": 1.0}
