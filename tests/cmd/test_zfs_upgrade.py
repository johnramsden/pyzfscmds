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


@pytest.mark.parametrize("supported", [True, False])
def test_zfs_upgrade_list_successful(supported):
    pyzfscmds.cmd.zfs_upgrade_list(supported=supported)


@require_zpool
@require_test_dataset
def test_zfs_upgrade_list_successful(zpool):
    pyzfscmds.cmd.zfs_upgrade(target=zpool)
