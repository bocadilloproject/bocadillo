import pytest

from bocadillo import API


def test_redirect_by_route_name(api: API):
    @api.route('/home', name='home')
    def home(req, res):
        res.text = 'You are home!'

    @api.route('/')
    def index(req, res):
        api.redirect(name='home')

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.text == 'You are home!'


def test_if_redirect_to_non_existing_route_then_404(api: API):
    @api.route('/')
    def index(req, res):
        api.redirect(name='home')

    response = api.client.get('/')
    assert response.status_code == 404


def test_redirect_to_internal_url(api: API):
    @api.route('/about/{who}')
    def index(req, res, who):
        res.text = who

    @api.route('/')
    def index(req, res):
        api.redirect(url='/about/me')

    response = api.client.get('/')
    assert response.status_code == 200
    assert response.text == 'me'


def test_if_redirect_to_non_matching_internal_url_then_404(api: API):
    @api.route('/')
    def index(req, res):
        api.redirect(url='/about/me')

    response = api.client.get('/')
    assert response.status_code == 404


def test_redirect_to_external_url(api: API):
    external_url = 'https://httpbin.org/status/202'

    @api.route('/')
    def index(req, res):
        api.redirect(url=external_url)

    # NOTE: cannot follow redirect here, because the TestClient
    # prepends the base_url (http://testserver) to any request made, including
    # the redirected request.
    response = api.client.get('/', allow_redirects=False)
    assert response.status_code == 302
    assert response.headers['location'] == external_url


def test_at_least_one_of_name_or_url_must_be_given(api: API):
    @api.route('/')
    def index(req, res):
        api.redirect()

    with pytest.raises(AssertionError) as ctx:
        api.client.get('/')
    assert all(item in str(ctx.value) for item in ('url', 'expected', 'name'))
