import datetime

import pytest

import pyzfsutils.cmd

import os

module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")

"""zfs commands tests"""


require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


def test_zfs_mount_list_successful():
    pyzfsutils.cmd.zfs_mount_list()


@require_zpool
@require_test_dataset
def test_zfs_mount_unmount_successful(zpool, test_dataset):

    dataset_name = "/".join([zpool,
                             test_dataset,
                             f"pyzfsutils-{datetime.datetime.now().isoformat()}"])
    print(f"Creating {dataset_name}")

    pyzfsutils.cmd.zfs_create_dataset(dataset_name,
                                      properties=["canmount=noauto"])

    pyzfsutils.cmd.zfs_mount(target=dataset_name)

    assert "yes" in pyzfsutils.cmd.zfs_get(dataset_name,
                                           columns=["value"],
                                           properties=["mounted"])

    pyzfsutils.cmd.zfs_unmount(dataset_name)

    assert "no" in pyzfsutils.cmd.zfs_get(dataset_name,
                                          columns=["value"],
                                          properties=["mounted"])
