import datetime

import pytest

import pyzfsutils.cmd
import pyzfsutils.utility as zfs_utility

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


@require_zpool
@require_test_dataset
@pytest.fixture(scope="function")
def clone_dataset(zpool, test_dataset):
    dataset_name = "/".join([zpool,
                             test_dataset,
                             f"pyzfsutils-cloneds-{datetime.datetime.now().isoformat()}"])

    pyzfsutils.cmd.zfs_create_dataset(dataset_name,
                                      create_parent=True)

    return dataset_name


def create_clone(dataset_name, snapname, properties: list = None, create_parent=False):
    clone_root = zfs_utility.dataset_parent(dataset_name)
    clone_suffix = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    try:
        pyzfsutils.cmd.zfs_snapshot(dataset_name, snapname)
        pyzfsutils.cmd.zfs_clone(f"{dataset_name}@{snapname}",
                                 f"{clone_root}/{clone_suffix}",
                                 properties=properties,
                                 create_parent=create_parent)
    except (RuntimeError, TypeError):
        raise


@pytest.mark.parametrize("properties", [None, [], ["compression=off"]])
@pytest.mark.parametrize("create_parent", [True, False])
@require_zpool
@require_test_dataset
def test_zfs_clone_successful(clone_dataset, properties, create_parent):

    snapname = f"pyzfsutils-{datetime.datetime.now().isoformat()}"

    create_clone(clone_dataset, snapname,
                 properties=properties, create_parent=create_parent)


@pytest.mark.parametrize("snapname", [
    None, f"@pyzfsutils-test", "", "@"
])
@pytest.mark.parametrize("properties", [None, [], ["compression=off"]])
@pytest.mark.parametrize("create_parent", [True, False])
@require_zpool
@require_test_dataset
def test_zfs_clone_fails(clone_dataset, snapname, properties, create_parent):

    with pytest.raises((TypeError, RuntimeError)):
        create_clone(clone_dataset,
                     snapname,
                     properties=properties,
                     create_parent=create_parent)
