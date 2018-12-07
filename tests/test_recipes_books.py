import pytest

from bocadillo import API
from bocadillo.recipes import Recipe, RecipeBook


@pytest.fixture
def numbers():

    integers = Recipe('integers')

    @integers.route('/{x}')
    async def convert(req, res, x):
        res.media = {'value': int(float(x))}

    floats = Recipe('floats')

    @floats.route('/{x}')
    async def convert(req, res, x):
        res.media = {'value': float(x)}

    return RecipeBook(integers, floats, prefix='/numbers')


def test_recipe_book(api: API, numbers):
    api.recipe(numbers)

    response = api.client.get('/numbers/integers/3.5')
    assert response.status_code == 200
    assert response.json() == {'value': 3}

    response = api.client.get('/numbers/floats/1')
    assert response.status_code == 200
    assert response.json() == {'value': 1.0}
