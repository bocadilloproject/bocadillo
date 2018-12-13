import bocadillo


def test_api_class_is_available():
    assert hasattr(bocadillo, "API")


def test_static_is_available():
    assert hasattr(bocadillo, "static")
