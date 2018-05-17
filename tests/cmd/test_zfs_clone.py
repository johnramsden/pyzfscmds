import datetime
import os

import pytest

import pyzfscmds.cmd
import pyzfscmds.utility as zfs_utility

module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


@require_zpool
@require_test_dataset
@pytest.fixture(scope="function")
def clone_dataset(zpool, test_dataset):
    dataset_name = "/".join([zpool,
                             test_dataset,
                             f"pyzfscmds-cloneds-{datetime.datetime.now().isoformat()}"])

    pyzfscmds.cmd.zfs_create_dataset(dataset_name,
                                     create_parent=True)

    return dataset_name


def create_clone(dataset_name, snapname, properties: list = None, create_parent=False):
    clone_root = zfs_utility.dataset_parent(dataset_name)
    clone_suffix = f"pyzfscmds-{datetime.datetime.now().isoformat()}"
    try:
        pyzfscmds.cmd.zfs_snapshot(dataset_name, snapname)
        pyzfscmds.cmd.zfs_clone(f"{dataset_name}@{snapname}",
                                f"{clone_root}/{clone_suffix}",
                                properties=properties,
                                create_parent=create_parent)
    except (RuntimeError, TypeError):
        raise

    return f"{clone_root}/{clone_suffix}"


@pytest.mark.parametrize("properties", [None, [], ["compression=off"]])
@pytest.mark.parametrize("create_parent", [True, False])
@require_zpool
@require_test_dataset
def test_zfs_clone_successful(clone_dataset, properties, create_parent):
    create_clone(clone_dataset,
                 f"pyzfscmds-{datetime.datetime.now().isoformat()}",
                 properties=properties, create_parent=create_parent)


@pytest.mark.parametrize("snapname", [
    None, f"@pyzfscmds-test", "", "@"
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


@require_zpool
@require_test_dataset
def test_zfs_promote_clone_successful(clone_dataset):
    pyzfscmds.cmd.zfs_promote(
        create_clone(clone_dataset,
                     f"pyzfscmds-{datetime.datetime.now().isoformat()}"))
