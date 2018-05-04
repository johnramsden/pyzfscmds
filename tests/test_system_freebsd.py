import pytest

import pyzfsutils.system.freebsd as zfsfreebsd

require_root_dataset = pytest.mark.require_root_dataset
require_zpool_root_mountpoint = pytest.mark.require_zpool_root_mountpoint

"""zfs freebsd tests"""


@require_zpool_root_mountpoint
@require_root_dataset
def test_freebsd_mount(zpool_root_mountpoint, root_dataset):
    assert root_dataset == zfsfreebsd.mountpoint_dataset(zpool_root_mountpoint)


def test_freebsd_mount_failure():
    assert zfsfreebsd.mountpoint_dataset("/garbage/mountpoint") is None
