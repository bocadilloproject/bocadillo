import pytest

from bocadillo import App, Recipe
from tests.conftest import TemplateWrapper


def test_use_template_string():
    numbers = Recipe("numbers")
    with pytest.deprecated_call():
        html = numbers.template_string("<h1>{{ title }}</h1>", title="Numbers")
    assert html == "<h1>Numbers</h1>"


def test_if_templates_dir_is_that_of_api_by_default(app: App):
    numbers = Recipe("numbers")
    app.recipe(numbers)
    with pytest.deprecated_call():
        assert numbers.templates_dir == app.templates_dir


def test_if_templates_dir_given_then_it_is_used(app: App):
    other_dir = "my_recipe/templates"
    numbers = Recipe("numbers", templates_dir=other_dir)
    app.recipe(numbers)
    with pytest.deprecated_call():
        assert numbers.templates_dir == other_dir != app.templates_dir


def test_render_template_in_recipe_route(
    template_file: TemplateWrapper, app: App
):
    numbers = Recipe("numbers")

    @numbers.route("/")
    async def get_numbers(req, res):
        with pytest.deprecated_call():
            res.html = await numbers.template(
                template_file.name, **template_file.context
            )

    app.recipe(numbers)

    response = app.client.get("/numbers/")
    assert response.status_code == 200
    assert response.text == template_file.rendered


def test_render_sync_template_in_recipe_route(
    template_file: TemplateWrapper, app: App
):
    numbers = Recipe("numbers")

    @numbers.route("/sync")
    def get_numbers_sync(req, res):
        with pytest.deprecated_call():
            res.html = numbers.template_sync(
                template_file.name, **template_file.context
            )

    app.recipe(numbers)

    response = app.client.get("/numbers/sync")
    assert response.status_code == 200
    assert response.text == template_file.rendered


def test_use_url_for(app: App):
    foo = Recipe("foo")

    @foo.route("/bar")
    async def bar(req, res):
        pass

    @foo.route("/fez")
    async def fez(req, res):
        with pytest.deprecated_call():
            res.html = foo.template_string(
                "<a href=\"{{ url_for('foo:bar') }}\">To bar</a>"
            )

    app.recipe(foo)

    response = app.client.get("/foo/fez")
    assert response.status_code == 200
    assert response.text == '<a href="/foo/bar">To bar</a>'
