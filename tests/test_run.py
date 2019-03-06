import os

import pytest

from bocadillo import App
from tests.utils import env


def test_if_port_env_var_is_set_then_host_is_any_and_port_is_env_var(app: App):
    with env("PORT", "4242"):

        def run(app, host, port, **kwargs):
            assert host == "0.0.0.0"
            assert port == 4242
            assert app == app

        app.run(_run=run)


def test_if_port_env_var_is_set_then_specified_host_is_used(app: App):
    with env("PORT", "4242"):

        def run(app, host, **kwargs):
            assert host == "example.com"

        app.run(_run=run, host="example.com")


def test_host_is_localhost_by_default(app: App):
    def run(app, host, **kwargs):
        assert host == "127.0.0.1"

    app.run(_run=run)


def test_port_is_8000_by_default(app: App):
    def run(app, port, **kwargs):
        assert port == 8000

    app.run(_run=run)


def test_debug_mode_disabled_by_default(app: App):
    def run(app, **kwargs):
        pass

    assert not app.debug
    app.run(_run=run)
    assert not app.debug


def test_if_debug_then_debug_mode_enabled(app: App):
    def run(app, **kwargs):
        pass

    assert not app.debug
    app.run(debug=True, _run=run)
    assert app.debug


def test_if_debug_env_var_set_then_debug_mode_enabled(app: App):
    os.environ["BOCADILLO_DEBUG"] = "1"
    try:
        assert not app.debug
        app.run(_run=lambda app, **kwargs: None)
        assert app.debug
    finally:
        os.environ.pop("BOCADILLO_DEBUG")


def test_if_debug_then_app_given_as_import_string(app: App):
    def run(app, **kwargs):
        assert isinstance(app, str)
        assert app.endswith(":app")

    app.run(debug=True, _run=run)


def test_if_debug_then_static_files_auto_refresh(app: App):
    def run(app, **kwargs):
        pass

    app.run(debug=True, _run=run)
    for static_app in app._static_apps.values():
        assert static_app.autorefresh


def test_declared_as(app: App):
    def run(app, **kwargs):
        assert app.endswith(":application")

    app.run(debug=True, declared_as="application", _run=run)


def test_if_import_string_unknown_then_no_debug_warning_raised(app: App):
    def run(app, **kwargs):
        pass

    app.import_string = None
    with pytest.warns(UserWarning):
        app.run(debug=True, _run=run)
