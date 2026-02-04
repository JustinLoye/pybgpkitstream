import sys


def test_smoke():
    """A minimal test to ensure the package and its main components can be imported."""
    import pybgpkitstream

    assert pybgpkitstream is not None


if __name__ == "__main__":
    test_smoke()
    sys.exit(0)
