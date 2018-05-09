import pytest
import datetime

import pyzfsutils.cmd

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


# @pytest.mark.parametrize("", [None, [""]])
@require_zpool
@require_test_dataset
def test_zfs_rollback_successful(zpool, test_dataset):

    dataset_name = "/".join([zpool,
                             test_dataset,
                             f"pyzfsutils-{datetime.datetime.now().isoformat()}"])
    snapname = f"pyzfsutils-{datetime.datetime.now().isoformat()}"

    pyzfsutils.cmd.zfs_create_dataset(dataset_name)
    pyzfsutils.cmd.zfs_snapshot(dataset_name, snapname)
    pyzfsutils.cmd.zfs_rollback("@".join([dataset_name, snapname]))
