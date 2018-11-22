import json

import pytest

from bocadillo import API, Media
from bocadillo.exceptions import UnsupportedMediaType


def test_defaults_to_json(api: API):
    data = {'message': 'hello'}

    @api.route('/')
    async def index(req, res):
        res.media = data

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.headers['content-type'] == Media.JSON
    assert response.json() == data


def test_can_specify_media_type_when_creating_the_api_object():
    API(media_type=Media.PLAIN_TEXT)


def test_media_type_is_accessible_on_api(api: API):
    assert hasattr(api, 'media')
    assert hasattr(api.media, 'type')


@pytest.mark.parametrize('media_type, expected_text', [
    (Media.JSON, json.dumps),
    (Media.PLAIN_TEXT, str),
    (Media.HTML, str),
])
def test_use_media_types(api: API, media_type, expected_text):
    api.media.type = media_type
    data = {'message': 'hello'}

    @api.route('/')
    async def index(req, res):
        res.media = data

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.headers['content-type'] == media_type
    assert response.text == expected_text(data)


def test_add_and_use_custom_media_handler(api: API):
    def handle_foo(value: str) -> str:
        return f'FOO: {value}'

    foo_type = 'application/foo'
    api.media.handlers[foo_type] = handle_foo
    api.media.type = foo_type

    @api.route('/')
    async def index(req, res):
        res.media = 'bar'

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.headers['content-type'] == foo_type
    assert response.text == 'FOO: bar'


def test_if_media_type_not_supported_then_setting_it_raises_error(api: API):
    with pytest.raises(UnsupportedMediaType):
        api.media.type = 'application/foo'

    with pytest.raises(UnsupportedMediaType):
        API(media_type='application/foo')
