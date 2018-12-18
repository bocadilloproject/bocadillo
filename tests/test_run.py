from bocadillo import API
from tests.utils import env


def test_if_port_env_var_is_set_then_host_is_any_and_port_is_env_var(api: API):
    with env("PORT", "4242"):

        def run(app, host, port, **kwargs):
            assert host == "0.0.0.0"
            assert port == 4242
            assert app == api

        api.run(_run=run)


def test_if_port_env_var_is_set_then_specified_host_is_used(api: API):
    with env("PORT", "4242"):

        def run(app, host, **kwargs):
            assert host == "example.com"

        api.run(_run=run, host="example.com")


def test_host_is_localhost_by_default(api: API):
    def run(app, host, **kwargs):
        assert host == "127.0.0.1"

    api.run(_run=run)


def test_port_is_8000_by_default(api: API):
    def run(app, port, **kwargs):
        assert port == 8000

    api.run(_run=run)
