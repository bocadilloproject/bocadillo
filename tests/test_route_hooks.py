from bocadillo import API
from .utils import function_hooks, async_function_hooks, class_hooks


def test_can_use_function_flags(api: API):
    with function_hooks() as (before, after):

        @api.before(before)
        @api.after(after)
        @api.route('/foo')
        async def foo(req, res):
            pass

        api.client.get('/foo')


def test_use_hook_on_sync_function_view(api: API):
    with function_hooks() as (before, after):

        @api.before(before)
        @api.after(after)
        @api.route('/foo')
        def foo(req, res):
            pass

        api.client.get('/foo')


def test_can_pass_extra_args(api: API):
    with function_hooks(after_value=1) as (before, after):

        @api.before(before, True)  # positional
        @api.after(after, value=1)  # keyword
        @api.route('/foo')
        async def foo(req, res):
            pass

        api.client.get('/foo')


def test_hook_can_be_callable_class(api: API):
    with class_hooks() as (before, after):

        @api.before(before)
        @api.after(after)
        @api.route('/foo')
        async def foo(req, res):
            pass

        api.client.get('/foo')


def test_use_hook_on_class_based_view(api: API):
    with class_hooks() as (before, after):

        @api.before(before)
        @api.after(after)
        @api.route('/foo')
        class Foo:
            async def get(self, req, res):
                pass

        api.client.get('/foo')


def test_use_hook_on_method(api: API):
    with class_hooks() as (before, after):

        @api.route('/foo')
        class Foo:
            @api.before(before)
            @api.after(after)
            async def get(self, req, res):
                pass

        api.client.get('/foo')


def test_use_hook_on_sync_method(api: API):
    with class_hooks() as (before, after):

        @api.route('/foo')
        class Foo:
            @api.before(before)
            @api.after(after)
            def get(self, req, res):
                pass

        api.client.get('/foo')


def test_hooks_can_be_async(api: API):
    with async_function_hooks() as (before, after):

        @api.before(before)
        @api.after(after)
        @api.route('/foo')
        async def foo(req, res):
            pass

        api.client.get('/foo')


def test_before_does_not_run_if_method_not_allowed(api: API):
    with async_function_hooks(False, False) as (before, after):

        @api.before(before)
        @api.after(after)
        @api.route('/foo', methods=['get'])
        async def foo(req, res):
            pass

        response = api.client.put('/foo')
        assert response.status_code == 405
