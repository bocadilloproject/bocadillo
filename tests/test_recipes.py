from bocadillo import API
from bocadillo.recipes import Recipe


def test_can_register_recipe(api: API):
    numbers = Recipe('numbers')

    @numbers.route('/real')
    def real_numbers(req, res):
        pass

    api.recipe(numbers)

    response = api.client.get('/numbers/real')
    assert response.status_code == 200
