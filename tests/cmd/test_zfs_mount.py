import datetime
import os

import pytest

import pyzfscmds.cmd

module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


def test_zfs_mount_list_successful():
    pyzfscmds.cmd.zfs_mount_list()


@require_zpool
@require_test_dataset
def test_zfs_mount_unmount_successful(zpool, test_dataset):
    dataset_name = "/".join([zpool,
                             test_dataset,
                             f"pyzfscmds-{datetime.datetime.now().isoformat()}"])
    print(f"Creating {dataset_name}")

    pyzfscmds.cmd.zfs_create_dataset(dataset_name,
                                     properties=["canmount=noauto"])

    pyzfscmds.cmd.zfs_mount(target=dataset_name)

    assert "yes" in pyzfscmds.cmd.zfs_get(dataset_name,
                                          columns=["value"],
                                          properties=["mounted"])

    pyzfscmds.cmd.zfs_unmount(dataset_name)

    assert "no" in pyzfscmds.cmd.zfs_get(dataset_name,
                                         columns=["value"],
                                         properties=["mounted"])
