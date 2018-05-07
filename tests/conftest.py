import pytest


def pytest_addoption(parser):
    parser.addoption("--root-dataset", action="store", default=None,
                     help="Specify a root dataset to use.")
    parser.addoption("--zpool-root-mountpoint", action="store", default=None,
                     help="Specify a root mountpoint to use.")
    parser.addoption("--zpool", action="store", default=None,
                     help="Specify a pool to use.")
    parser.addoption("--unsafe", action="store_true",
                     help="Specify test 'unsafe' commands.")


def pytest_runtest_setup(item):
    if 'require_root_dataset' in item.keywords and not item.config.getvalue("root_dataset"):
        pytest.skip("Need --root-dataset option to run")

    if 'require_zpool_root_mountpoint' in item.keywords and not item.config.getvalue(
                                                                    "zpool_root_mountpoint"):
        pytest.skip("Need --zpool-root-mountpoint option to run")

    if 'require_zpool' in item.keywords and not item.config.getvalue("zpool"):
        pytest.skip("Need --zpool option to run")

    if 'require_unsafe' in item.keywords and not item.config.getvalue("unsafe"):
        pytest.skip("Need --unsafe option to run")


@pytest.fixture
def root_dataset(request):
    """Specify a root dataset to use."""
    return request.config.getoption("--root-dataset")


@pytest.fixture
def zpool_root_mountpoint(request):
    """Specify a root dataset to use."""
    return request.config.getoption("--zpool-root-mountpoint")


@pytest.fixture
def zpool(request):
    """Specify a root dataset to use."""
    return request.config.getoption("--zpool")


@pytest.fixture
def unsafe(request):
    """Specify test 'unsafe' commands."""
    return request.config.getoption("--unsafe")
