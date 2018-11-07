from tests.utils import RouteBuilder


def test_if_nothing_set_then_response_is_empty_json_object(builder: RouteBuilder):
    builder.function_based('/')
    response = builder.api.client.get('/')
    assert response.json() == {}


def test_if_content_set_then_response_is_plain_text(builder):
    builder.function_based('/', res={'content': 'foo'})
    response = builder.api.client.get('/')
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.text == 'foo'


def test_if_media_set_then_response_is_json(builder):
    builder.function_based('/', res={'media': {'foo': 'bar'}})
    response = builder.api.client.get('/')
    assert response.json() == {'foo': 'bar'}


def test_if_html_set_then_response_is_html(builder):
    builder.function_based('/', res={'html': '<h1>Foo</h1>'})
    response = builder.api.client.get('/')
    assert response.headers['Content-Type'] == 'text/html'
    assert response.text == '<h1>Foo</h1>'


def test_last_response_setter_called_has_priority(builder):
    builder.function_based('/', res={
        'media': {'foo': 'bar'},
        'content': 'foo',
    })
    response = builder.api.client.get('/')
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.text == 'foo'

    builder.function_based('/', res={
        'content': 'foo',
        'media': {'foo': 'bar'},
    })
    response = builder.api.client.get('/')
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json() == {'foo': 'bar'}
