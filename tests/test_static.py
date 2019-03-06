import pytest

from bocadillo import App, static
from bocadillo.testing import create_client

FILE_DIR = "js"
FILE_NAME = "foo.js"
FILE_CONTENTS = "console.log('foo!');"


def _create_asset(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENTS)
    return asset


def test_assets_are_served_at_static_by_default(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("static")
    _create_asset(static_dir)

    app = App(static_dir=str(static_dir))
    client = create_client(app)

    response = client.get(f"/static/{FILE_DIR}/{FILE_NAME}")
    assert response.status_code == 200
    assert response.text == FILE_CONTENTS


def test_if_asset_does_not_exist_then_404(app: App, client):
    assert client.get(f"/static/{FILE_DIR}/{FILE_NAME}").status_code == 404


def test_customize_static_root(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("static")
    _create_asset(static_dir)

    app = App(static_dir=str(static_dir), static_root="assets")
    client = create_client(app)

    assert client.get(f"/static/{FILE_DIR}/{FILE_NAME}").status_code == 404
    response = client.get(f"/assets/{FILE_DIR}/{FILE_NAME}")
    assert response.status_code == 200
    assert response.text == FILE_CONTENTS


def test_if_static_dir_is_none_then_no_assets_served(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("static")
    _create_asset(static_dir)

    app = App(static_dir=None)
    client = create_client(app)

    assert client.get(f"/static/{FILE_DIR}/{FILE_NAME}").status_code == 404


def test_static_root_defaults_to_static_dir(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("foo")
    _create_asset(static_dir)

    app = App(static_dir=str(static_dir), static_root=None)
    client = create_client(app)

    response = client.get(f"{static_dir}/{FILE_DIR}/{FILE_NAME}")
    assert response.status_code == 200


def test_mount_extra_static_files_dirs(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("staticfiles")
    _create_asset(static_dir)

    app = App(static_dir=None)
    app.mount("assets", static(str(static_dir)))
    client = create_client(app)

    response = client.get(f"/assets/{FILE_DIR}/{FILE_NAME}")
    assert response.status_code == 200
    assert response.text == FILE_CONTENTS


def test_if_static_dir_does_not_exist_then_no_files_mounted():
    with pytest.warns(None) as record:
        App(static_dir="foo")
    assert len(record) == 0


def test_whitenoise_config():
    app = App(static_root="static", static_config={"max_age": 30})
    whitenoise = app._prefix_to_app["/static"]
    assert whitenoise.max_age == 30
