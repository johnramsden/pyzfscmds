"""zfs utilities tests"""

import datetime

import pytest

import pyzfsutils.cmd
import pyzfsutils.utility as zfs_utility

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


"""Test variables"""

test_dataset_names = {
    "boot_environment_root": "zpool/ROOT",
    "boot_environment": "default",
    "root": "zpool/ROOT/default"
}

"""
Tests for function: pyzfsutils.lib.zfs.utility.is_snapshot()
"""


# TODO: Finish
@pytest.mark.parametrize("snapname", [
    "", "@", "fakename/dataset"
])
def test_is_not_snapshot(snapname):
    assert zfs_utility.is_snapshot(snapname) is False


@require_zpool
@require_test_dataset
def test_is_snapshot(zpool, test_dataset):
    snapname = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    dataset = "/".join([zpool, test_dataset])

    pyzfsutils.cmd.zfs_snapshot(dataset, snapname)

    assert zfs_utility.is_snapshot(f"{dataset}@{snapname}")


"""
Tests for function: pyzfsutils.lib.zfs.utility.is_clone()
"""


@require_zpool
@require_test_dataset
def test_is_not_clone_valid_option(zpool, test_dataset):
    """Make sure valid ZFS options give 'False' if they're not a clone."""
    snapname = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    dataset = "/".join([zpool, test_dataset])

    pyzfsutils.cmd.zfs_snapshot(dataset, snapname)

    try:
        dataset_is_clone = zfs_utility.is_clone(f"{dataset}@{snapname}")
        print(dataset_is_clone)
    except RuntimeError:
        raise

    assert not dataset_is_clone


@pytest.mark.parametrize("clonename", ["", "@", "fakename/dataset"])
def test_is_not_clone_invalid_option(clonename):
    """Make sure invalid ZFS options raise a RuntimeError."""
    with pytest.raises(RuntimeError):
        zfs_utility.is_clone(clonename)


@require_zpool
@require_test_dataset
def test_is_clone(zpool, test_dataset):
    dataset = "/".join([zpool, test_dataset])
    clone_root = zfs_utility.dataset_parent(dataset)

    snapname = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    pyzfsutils.cmd.zfs_snapshot(dataset, snapname)

    clone_name = f"{clone_root}/pyzfsutils-{datetime.datetime.now().isoformat()}"
    pyzfsutils.cmd.zfs_clone(f"{dataset}@{snapname}", clone_name)

    assert zfs_utility.is_clone(clone_name)


"""
Tests for function: pyzfsutils.lib.zfs.utility.dataset_parent()
"""


def test_dataset_parent():
    assert zfs_utility.dataset_parent(
        test_dataset_names['root']) == test_dataset_names['boot_environment_root']


"""
Tests for function: pyzfsutils.lib.zfs.utility.dataset_child_name()
"""


def test_dataset_child_name():
    assert zfs_utility.dataset_child_name(
        test_dataset_names['root']) == test_dataset_names['boot_environment']


"""
Tests for function: pyzfsutils.lib.zfs.utility.parent_dataset()
"""


def test_snapshot_parent_dataset():
    assert zfs_utility.snapshot_parent_dataset(
        f"{test_dataset_names['root']}@my-snap") == test_dataset_names['root']
