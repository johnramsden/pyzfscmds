import pytest

import pyzfsutils.cmd

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


@pytest.mark.parametrize("supported", [True, False])
def test_zfs_upgrade_list_successful(supported):
    pyzfsutils.cmd.zfs_upgrade_list(supported=supported)


@require_zpool
@require_test_dataset
def test_zfs_upgrade_list_successful(zpool):
    pyzfsutils.cmd.zfs_upgrade(target=zpool)
