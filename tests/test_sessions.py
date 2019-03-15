import pytest

from bocadillo import App, view
from bocadillo.compat import nullcontext
from bocadillo.sessions import MissingSecretKey
from bocadillo.testing import create_client
from bocadillo.utils import override_env


def test_sessions_enabled_no_secret_key():
    with pytest.raises(MissingSecretKey):
        App(enable_sessions=True)


def test_sessions_enabled_secret_key_empty():
    with override_env("SECRET_KEY", ""):
        with pytest.raises(MissingSecretKey):
            App(enable_sessions=True)


@pytest.mark.parametrize(
    "ctx, config",
    (
        [override_env("SECRET_KEY", "not-so-secret"), {}],
        [nullcontext(), {"secret_key": "not-so-secret"}],
    ),
)
def test_sessions_enabled_secret_key_present(ctx, config):
    with ctx:
        app = App(enable_sessions=True, sessions_config=config)

        @app.route("/set")
        @view(methods=["post"])
        async def set_session(req, res):
            req.session["data"] = "something"
            res.text = "Saved"

        @app.route("/")
        async def index(req, res):
            data = req.session["data"]
            res.text = f"Hello {data}"

        client = create_client(app)
        client.post("/set")
        response = client.get("/")
        assert "something" in response.text
        assert "session" in response.cookies
