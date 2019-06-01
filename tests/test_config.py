import pytest

from bocadillo import configure, create_client, settings


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


@pytest.mark.parametrize("positional", (True, False))
def test_settings(raw_app, positional: bool):
    class Settings:
        ONE = "one"
        _IGNORED = "ignored"
        ignored_too = "ignored too"

    args = [raw_app]
    kwargs = {"two": "two", "settings": Settings()}
    if positional:
        args.append(kwargs.pop("settings"))

    configure(*args, **kwargs)

    assert settings.ONE == "one"
    assert settings.TWO == "two"
    for name in "two", "three", "_IGNORED", "ignored_too", "IGNORED_TOO":
        assert name not in settings

    settings.ONE = 1
    assert settings.ONE == 1
