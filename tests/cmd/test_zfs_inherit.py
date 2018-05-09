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


@pytest.mark.parametrize("prop", ["setuid", "acltype", "compression"])
@require_zpool
@require_test_dataset
def test_zfs_inherit_successful(zpool, test_dataset, prop):

    dataset_name = f"pyzfsutils-{datetime.datetime.now().isoformat()}"

    pyzfsutils.cmd.zfs_create_dataset(f"{zpool}/{test_dataset}/{dataset_name}")
    pyzfsutils.cmd.zfs_inherit(prop, f"{zpool}/{test_dataset}/{dataset_name}")
