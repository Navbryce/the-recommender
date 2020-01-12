def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 4

def test_build_trigger():
    assert inc(4) == 5