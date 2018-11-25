from contextlib import contextmanager
from typing import Any

from bocadillo import API


@contextmanager
def function_hooks(before_value: Any = True, after_value: Any = True):
    flags = {'before': False, 'after': False}

    def before(req, res, params, value=before_value):
        nonlocal flags
        assert not flags['after']
        flags['before'] = value

    def after(req, res, params, value=after_value):
        nonlocal flags
        assert flags['before']
        flags['after'] = value

    yield before, after

    assert flags['before'] == before_value
    assert flags['after'] == after_value


@contextmanager
def async_function_hooks(expected_before=True, expected_after=True):
    flags = {'before': False, 'after': False}

    async def before(req, res, params):
        nonlocal flags
        assert not flags['after']
        flags['before'] = True

    async def after(req, res, params):
        nonlocal flags
        assert flags['before']
        flags['after'] = True

    yield before, after

    assert flags['before'] is expected_before
    assert flags['after'] is expected_after


@contextmanager
def class_hooks():
    flags = {'before': False, 'after': False}

    class SetFlag:
        def __init__(self, flag, value):
            self.flag = flag
            self.value = value

        def __call__(self, req, res, params):
            nonlocal flags
            flags[self.flag] = self.value

    yield SetFlag('before', True), SetFlag('after', True)

    assert flags['before']
    assert flags['after']


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
