import pytest

import pyzfsutils.system.linux as zfslinux
import pyzfsutils.check

require_root_dataset = pytest.mark.require_root_dataset
require_zpool_root_mountpoint = pytest.mark.require_zpool_root_mountpoint

"""zfs linux tests"""


@require_zpool_root_mountpoint
@require_root_dataset
def test_linux_mount(root_dataset, zpool_root_mountpoint):
    assert root_dataset == zfslinux.mountpoint_dataset(zpool_root_mountpoint)


def test_linux_mount_failure():
    assert zfslinux.mountpoint_dataset("/garbage/mountpoint") is None


def test_system_startup_check():
    assert pyzfsutils.check.check_valid_system() == "linux"
