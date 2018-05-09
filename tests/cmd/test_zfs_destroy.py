import datetime

import pytest

import pyzfsutils.cmd
import pyzfsutils.utility

import os

module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")


"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_unsafe = pytest.mark.require_unsafe
require_test_dataset = pytest.mark.require_test_dataset


@require_zpool
@require_unsafe
@require_test_dataset
def test_zfs_destroy_dataset_successful(zpool, test_dataset):
    # Cannot parameterize, must be unique
    dataset_name = "/".join([zpool,
                             test_dataset,
                             f"pyzfsutils-{datetime.datetime.now().isoformat()}"])
    print(f"Creating {dataset_name}")

    pyzfsutils.cmd.zfs_create_dataset(f"{dataset_name}/foo", create_parent=True)
    pyzfsutils.cmd.zfs_destroy(f"{dataset_name}", recursive_children=True)


@require_zpool
@require_unsafe
@require_test_dataset
def test_zfs_destroy_dataset_with_dependents(zpool, test_dataset):
    # Cannot parameterize, must be unique
    dataset_name = "/".join([zpool,
                             test_dataset,
                             f"pyzfsutils-{datetime.datetime.now().isoformat()}"])

    snap_name = f"pyzfsutils-snap-{datetime.datetime.now().isoformat()}"
    print(f"Creating {dataset_name}")
    """ Test will pass if create and destroy successful"""

    pyzfsutils.cmd.zfs_create_dataset(dataset_name)

    clone_root = pyzfsutils.utility.dataset_parent(dataset_name)
    clone_suffix = f"pyzfsutils-clone-{datetime.datetime.now().isoformat()}"
    try:
        pyzfsutils.cmd.zfs_snapshot(dataset_name, snap_name)
        pyzfsutils.cmd.zfs_clone(f"{dataset_name}@{snap_name}",
                                 f"{clone_root}/{clone_suffix}")
    except (RuntimeError, TypeError):
        raise

    pyzfsutils.cmd.zfs_destroy(f"{dataset_name}", recursive_dependents=True)


@pytest.mark.parametrize("name", [f"@pyzfsutils-test", "", "@"])
@require_zpool
@require_unsafe
def test_zfs_destroy_dataset_fails(zpool, name):
    print(f"Destroy non-existant dataset {zpool}/{name}")
    """ Test will pass if clone fails"""

    with pytest.raises((TypeError, RuntimeError)):
        pyzfsutils.cmd.zfs_destroy(f"{zpool}/{name}")
