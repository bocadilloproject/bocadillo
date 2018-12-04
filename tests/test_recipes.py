import pytest

from bocadillo import API
from bocadillo.recipes import Recipe
from tests.conftest import TemplateWrapper


def test_if_prefix_not_given_then_routes_mounted_at_slash_name(api: API):
    numbers = Recipe('numbers')

    @numbers.route('/real', name='real-numbers')
    def real_numbers(req, res):
        pass

    api.recipe(numbers)

    assert api.url_for('real-numbers') == '/numbers/real'


def test_if_prefix_then_routes_mounted_at_prefix(api: API):
    numbers = Recipe('numbers', prefix='/numbers-yo')

    @numbers.route('/real', name='real-numbers')
    def real_numbers(req, res):
        pass

    api.recipe(numbers)

    assert api.url_for('real-numbers') == '/numbers-yo/real'


def test_if_prefix_does_not_start_with_slash_then_error_raised():
    with pytest.raises(AssertionError):
        Recipe('numbers', prefix='numbers-yo')


def test_use_template_string():
    numbers = Recipe('numbers')
    html = numbers.template_string('<h1>{{ title }}</h1>', title='Numbers')
    assert html == '<h1>Numbers</h1>'


def test_if_render_template_then_templates_dir_is_that_of_api(api: API):
    numbers = Recipe('numbers')
    api.recipe(numbers)
    assert numbers.templates_dir == api.templates_dir


def test_render_template_in_recipe_route(
    template_file: TemplateWrapper, api: API
):
    numbers = Recipe('numbers')

    @numbers.route('/')
    async def get_numbers(req, res):
        res.html = await numbers.template(
            template_file.name, **template_file.context
        )

    api.recipe(numbers)

    response = api.client.get('/numbers/')
    assert response.status_code == 200
    assert response.text == template_file.rendered


def test_render_sync_template_in_recipe_route(
    template_file: TemplateWrapper, api: API
):
    numbers = Recipe('numbers')

    @numbers.route('/sync')
    def get_numbers_sync(req, res):
        res.html = numbers.template_sync(
            template_file.name, **template_file.context
        )

    api.recipe(numbers)

    response = api.client.get('/numbers/sync')
    assert response.status_code == 200
    assert response.text == template_file.rendered
