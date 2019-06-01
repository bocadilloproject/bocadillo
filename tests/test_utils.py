import os

from bocadillo.utils import override_env


def test_override_env():
    var = "VARIABLE"

    def getvar():
        return os.getenv(var)

    initial = getvar()

    with override_env(var, "initial"):
        with override_env(var, "value"):
            assert getvar() == "value"
        assert getvar() == "initial"

    assert getvar() == initial
