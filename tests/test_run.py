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


def test_if_debug_then_static_files_auto_refresh(app: App):
    def run(app, **kwargs):
        for static_app in app._static_apps.values():
            assert static_app.autorefresh

    app.run(debug=True, _run=run)
