from bocadillo import API


def test_if_nothing_set_then_response_is_empty(api: API):
    @api.route('/')
    async def index(req, res):
        pass

    response = api.client.get('/')
    assert not response.text


def test_if_status_code_is_no_content_then_no_content_type_set(api: API):
    @api.route('/')
    async def index(req, res):
        res.status_code = 204

    response = api.client.get('/')
    assert not response.text
    assert response.headers.get('content-type') is None


def test_content_type_defaults_to_plaintext(api: API):
    @api.route('/')
    def index(req, res):
        res.content = 'Something magical'
        # make sure no content-type is set before leaving the view
        res.headers.pop('Content-Type', None)

    response = api.client.get('/')
    assert response.headers['Content-Type'] == 'text/plain'


def test_if_text_set_then_response_is_plain_text(builder):
    builder.function_based('/', res={'text': 'foo'})
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
        'text': 'foo',
    })
    response = builder.api.client.get('/')
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.text == 'foo'

    builder.function_based('/', res={
        'text': 'foo',
        'media': {'foo': 'bar'},
    })
    response = builder.api.client.get('/')
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json() == {'foo': 'bar'}
