from subprocess import call


def test_can_call_boca():
    assert call(['boca']) == 0
