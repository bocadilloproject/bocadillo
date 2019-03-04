from bocadillo import App, hooks
from .utils import function_hooks, async_function_hooks, class_hooks


def test_can_use_function_hooks(app: App):
    with function_hooks() as (before, after):

        @app.route("/foo")
        @hooks.before(before)
        @hooks.after(after)
        async def foo(req, res):
            pass

        app.client.get("/foo")


def test_use_hook_on_sync_function_view(app: App):
    with function_hooks() as (before, after):

        @app.route("/foo")
        @hooks.before(before)
        @hooks.after(after)
        def foo(req, res):
            pass

        app.client.get("/foo")


def test_can_pass_extra_args(app: App):
    with function_hooks(after_value=1) as (before, after):

        @app.route("/foo")
        class Foo:
            @hooks.before(before, True)  # positional
            @hooks.after(after, value=1)  # keyword
            async def get(self, req, res):
                pass

        app.client.get("/foo")


def test_hook_can_be_callable_class(app: App):
    with class_hooks() as (before, after):

        @app.route("/foo")
        class Foo:
            @hooks.before(before)
            @hooks.after(after)
            async def get(self, req, res):
                pass

        app.client.get("/foo")


def test_use_hook_on_view_class(app: App):
    with class_hooks() as (before, after):

        @app.route("/foo")
        @hooks.before(before)
        @hooks.after(after)
        class Foo:
            async def get(self, req, res):
                pass

        app.client.get("/foo")


def test_use_hook_on_method(app: App):
    with class_hooks() as (before, after):

        @app.route("/foo")
        class Foo:
            @hooks.before(before)
            @hooks.after(after)
            async def get(self, req, res):
                pass

        app.client.get("/foo")


def test_use_hook_on_sync_method(app: App):
    with class_hooks() as (before, after):

        @app.route("/foo")
        class Foo:
            @hooks.before(before)
            @hooks.after(after)
            def get(self, req, res):
                pass

        app.client.get("/foo")


def test_hooks_can_be_async(app: App):
    with async_function_hooks() as (before, after):

        @app.route("/foo")
        @hooks.before(before)
        @hooks.after(after)
        async def foo(req, res):
            pass

        app.client.get("/foo")


def test_before_does_not_run_if_method_not_allowed(app: App):
    with async_function_hooks(False, False) as (before, after):

        @app.route("/foo")
        @hooks.before(before)
        @hooks.after(after)
        class Foo:
            async def get(self, req, res):
                pass

        response = app.client.put("/foo")
        assert response.status_code == 405
