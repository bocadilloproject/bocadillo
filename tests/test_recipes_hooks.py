from bocadillo import API
from bocadillo.recipes import Recipe


def test_on_async_function_view(api: API):
    numbers = Recipe('numbers')

    before_called = False
    after_called = False

    async def before(req, res, params):
        nonlocal before_called
        before_called = True

    async def after(req, res, params):
        nonlocal after_called
        after_called = True

    @numbers.before(before)
    @numbers.after(after)
    @numbers.route('/real')
    async def real_numbers(req, res):
        pass

    api.recipe(numbers)
    api.client.get('/numbers/real')
    assert before_called
    assert after_called


def test_on_sync_function_view(api: API):
    numbers = Recipe('numbers')

    before_called = False
    after_called = False

    async def before(req, res, params):
        nonlocal before_called
        before_called = True

    async def after(req, res, params):
        nonlocal after_called
        after_called = True

    @numbers.before(before)
    @numbers.after(after)
    @numbers.route('/real')
    def real_numbers(req, res):
        pass

    api.recipe(numbers)
    api.client.get('/numbers/real')
    assert before_called
    assert after_called


def test_on_class_based_view(api: API):
    numbers = Recipe('numbers')

    before_called = False
    after_called = False

    async def before(req, res, params):
        nonlocal before_called
        before_called = True

    async def after(req, res, params):
        nonlocal after_called
        after_called = True

    @numbers.before(before)
    @numbers.route('/real')
    class RealNumbers:
        @numbers.after(after)
        async def get(self, req, res):
            pass

    api.recipe(numbers)
    api.client.get('/numbers/real')
    assert before_called
    assert after_called
