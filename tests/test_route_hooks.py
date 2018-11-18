from bocadillo import API
from bocadillo.exceptions import HTTPError


def test_can_use_simple_function(api: API):
    before_called = False
    after_called = False

    def set_before_flag(*args):
        nonlocal before_called
        assert not after_called
        before_called = True

    def set_after_flag(*args):
        nonlocal after_called
        assert before_called
        after_called = True

    @api.before(set_before_flag)
    @api.after(set_after_flag)
    @api.route('/foo')
    async def foo(req, res):
        pass

    api.client.get('/foo')
    assert before_called
    assert after_called


def test_can_pass_extra_args(api: API):
    before_called = False
    after_called = False

    def set_before_flag(req, res, view, params, value):
        nonlocal before_called
        assert not after_called
        before_called = value

    def set_after_flag(req, res, view, params, value):
        nonlocal after_called
        assert before_called
        after_called = value

    @api.before(set_before_flag, True)
    @api.after(set_after_flag, True)
    @api.route('/foo')
    async def foo(req, res):
        pass

    api.client.get('/foo')
    assert before_called
    assert after_called
