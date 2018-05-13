import pytest

import pyzfsutils.system.freebsd as zfsfreebsd

import os

module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")

require_root_dataset = pytest.mark.require_root_dataset
require_zpool_root_mountpoint = pytest.mark.require_zpool_root_mountpoint

"""zfs freebsd tests"""


@require_zpool_root_mountpoint
@require_root_dataset
def test_freebsd_mount(zpool_root_mountpoint, root_dataset):
    assert root_dataset == zfsfreebsd.mountpoint_dataset(zpool_root_mountpoint)


def test_freebsd_mount_failure():
    assert zfsfreebsd.mountpoint_dataset("/garbage/mountpoint") is None


def test_freebsd_dataset_mountpoint_failure():
    assert zfsfreebsd.dataset_mountpoint("garbage/dataset") is None


@require_zpool_root_mountpoint
@require_root_dataset
def test_freebsd_dataset_mountpoint(zpool_root_mountpoint, root_dataset):
    assert zpool_root_mountpoint == zfsfreebsd.dataset_mountpoint(root_dataset)
