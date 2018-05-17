import pytest

import pyzfscmds.cmd
import pyzfscmds.utility

# https://github.com/zfsonlinux/zfs/commit/2a8b84b747cb27a175aa3a45b8cdb293cde31886
zfs_support_version = '0.7.0'


def zfs_version_int(version):
    """
    Covert version to int
    https://stackoverflow.com/questions/41516633/how-to-convert-version-number-to-integer-value
    """

    # Remove patch
    version_no_patch = version.split('-')[0]

    l = [int(x, 10) for x in version_no_patch.split('.')]
    l.reverse()
    return sum(x * (100 ** i) for i, x in enumerate(l))


def pytest_addoption(parser):
    parser.addoption("--root-dataset", action="store", default=None,
                     help="Specify a root dataset to use.")

    parser.addoption("--zpool-root-mountpoint", action="store", default=None,
                     help="Specify a root mountpoint to use.")

    parser.addoption("--zpool", action="store", default=None, help="Specify a pool to use.")

    parser.addoption("--test-dataset", action="store", default=None,
                     help="Specify test dataset under the pool.")

    parser.addoption("--unsafe", action="store_true", help="Specify test 'unsafe' commands.")

    parser.addoption("--zfs-version", action="store", default='0.7.0',
                     help="Specify zfs version (linux).")


def pytest_runtest_setup(item):
    if 'require_root_dataset' in item.keywords and not item.config.getoption("--root-dataset"):
        pytest.skip("Need --root-dataset option to run")

    if 'require_zpool_root_mountpoint' in item.keywords and not item.config.getoption(
            "--zpool-root-mountpoint"):
        pytest.skip("Need --zpool-root-mountpoint option to run")

    if 'require_zpool' in item.keywords and not item.config.getoption("--zpool"):
        pytest.skip("Need --zpool option to run")

    if 'require_test_dataset' in item.keywords:
        if not item.config.getoption("--test-dataset"):
            pytest.skip("Need --test-dataset option to run")
        else:
            test_dataset_name = "/".join([
                item.config.getoption("--zpool"),
                item.config.getoption("--test-dataset")])
            if not pyzfscmds.utility.dataset_exists(test_dataset_name):
                pyzfscmds.cmd.zfs_create_dataset(test_dataset_name,
                                                 create_parent=True)

    if 'require_unsafe' in item.keywords and not item.config.getoption("--unsafe"):
        pytest.skip("Need --unsafe option to run")

    if 'require_zfs_version' in item.keywords:
        if zfs_version_int(
                item.config.getoption("--zfs-version")) < zfs_version_int(zfs_support_version):
            pytest.skip("Requires zfsonlinux > 0.7.0")


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
def test_dataset(request):
    """Specify a root dataset to use."""
    return request.config.getoption("--test-dataset")


@pytest.fixture
def unsafe(request):
    """Specify test 'unsafe' commands."""
    return request.config.getoption("--unsafe")


@pytest.fixture
def zfs_version(request):
    """Specify a root dataset to use."""
    return request.config.getoption("--zfs-version")
