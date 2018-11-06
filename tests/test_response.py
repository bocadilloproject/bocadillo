from bocadillo import API


def test_if_nothing_set_then_response_is_empty_json_object(api: API):
    @api.route('/')
    def index(req, res):
        pass

    response = api.client.get('/')
    assert response.json() == {}


def test_if_content_set_then_response_is_plain_text(api: API):
    @api.route('/')
    def index(req, res):
        res.content = 'foo'

    response = api.client.get('/')
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.text == 'foo'


def test_if_media_set_then_response_is_json(api: API):
    @api.route('/')
    def index(req, res):
        res.media = {'foo': 'bar'}

    response = api.client.get('/')
    assert response.json() == {'foo': 'bar'}


def test_if_html_set_then_response_is_html(api: API):
    @api.route('/')
    def index(req, res):
        res.html = '<h1>Foo</h1>'

    response = api.client.get('/')
    assert response.headers['Content-Type'] == 'text/html'
    assert response.text == '<h1>Foo</h1>'


def test_last_response_setter_called_has_priority(api: API):
    @api.route('/')
    def index(req, res):
        res.media = {'foo': 'bar'}
        res.content = 'foo'

    response = api.client.get('/')
    assert response.headers['Content-Type'] == 'text/plain'
    assert response.text == 'foo'
