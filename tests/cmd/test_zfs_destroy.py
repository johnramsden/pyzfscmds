import datetime

import pytest

import pyzfsutils.cmd
import pyzfsutils.utility

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_unsafe = pytest.mark.require_unsafe


@require_zpool
@require_unsafe
def test_zfs_destroy_dataset_successful(zpool):
    # Cannot parameterize, must be unique
    dataset_name = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    print(f"Creating {zpool}/{dataset_name}")
    """ Test will pass if create and destroy successful"""
    pyzfsutils.cmd.zfs_create_dataset(f"{zpool}/{dataset_name}/foo", create_parent=True)
    pyzfsutils.cmd.zfs_destroy(f"{zpool}/{dataset_name}", recursive_children=True)


@require_zpool
@require_unsafe
def test_zfs_destroy_dataset_with_dependents(zpool):
    # Cannot parameterize, must be unique
    dataset_name = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    snap_name = f"pyzfsutils-snap-{datetime.datetime.now().isoformat()}"
    print(f"Creating {zpool}/{dataset_name}")
    """ Test will pass if create and destroy successful"""
    pyzfsutils.cmd.zfs_create_dataset(f"{zpool}/{dataset_name}")

    clone_root = pyzfsutils.utility.dataset_parent(f"{zpool}/{dataset_name}")
    clone_suffix = f"pyzfsutils-clone-{datetime.datetime.now().isoformat()}"
    try:
        pyzfsutils.cmd.zfs_snapshot(f"{zpool}/{dataset_name}", snap_name)
        pyzfsutils.cmd.zfs_clone(f"{zpool}/{dataset_name}@{snap_name}",
                                 f"{clone_root}/{clone_suffix}")
    except (RuntimeError, TypeError):
        raise

    pyzfsutils.cmd.zfs_destroy(f"{zpool}/{dataset_name}", recursive_dependents=True)


@pytest.mark.parametrize("name", [f"@pyzfsutils-test", "", "@"])
@require_zpool
@require_unsafe
def test_zfs_create_dataset_fails(zpool, name):
    print(f"Destroy non-existant dataset {zpool}/{name}")
    """ Test will pass if clone fails"""

    with pytest.raises((TypeError, RuntimeError)):
        pyzfsutils.cmd.zfs_destroy(f"{zpool}/{name}")
