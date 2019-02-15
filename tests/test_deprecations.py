import pytest

from bocadillo import API, Recipe


@pytest.mark.parametrize("get_app", [lambda: API(), lambda: Recipe("tacos")])
def test_rendering_from_app_fails_with_friendly_message(get_app):
    app = get_app()
    with pytest.raises(NotImplementedError) as ctx:
        app.template_string("foo")
    message = str(ctx.value).lower()
    assert "please" in message
    assert "docs"
