import pytest

from bocadillo import configure, create_client


def test_cannot_reconfigure(app):
    with pytest.raises(RuntimeError):
        configure(app)


def test_must_be_configured_to_serve(raw_app):
    @raw_app.route("/")
    async def index(req, res):
        pass

    with pytest.raises(RuntimeError) as ctx:
        with create_client(raw_app):
            pass

    assert "configure(app)" in str(ctx.value)
