import pytest

import pyzfsutils.cmd

"""zfs commands tests"""


require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


def test_zfs_mount_list_successful():
    pyzfsutils.cmd.zfs_mount_list()
