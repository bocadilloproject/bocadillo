from bocadillo import API
from bocadillo.recipes import Recipe
from .utils import async_function_hooks


def test_on_async_function_view(api: API):
    numbers = Recipe('numbers')

    with async_function_hooks() as (before, after):

        @numbers.before(before)
        @numbers.after(after)
        @numbers.route('/real')
        async def real_numbers(req, res):
            pass

        api.recipe(numbers)
        api.client.get('/numbers/real')


def test_on_sync_function_view(api: API):
    numbers = Recipe('numbers')

    with async_function_hooks() as (before, after):

        @numbers.before(before)
        @numbers.after(after)
        @numbers.route('/real')
        def real_numbers(req, res):
            pass

        api.recipe(numbers)
        api.client.get('/numbers/real')


def test_on_class_based_view(api: API):
    numbers = Recipe('numbers')

    with async_function_hooks() as (before, after):

        @numbers.before(before)
        @numbers.route('/real')
        class RealNumbers:
            @numbers.after(after)
            async def get(self, req, res):
                pass

        api.recipe(numbers)
        api.client.get('/numbers/real')
