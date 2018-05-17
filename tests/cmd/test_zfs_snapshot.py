"""zfs snapshot tests"""

import datetime
import os

import pytest

import pyzfscmds.cmd

module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


# Incorrect options to test
@pytest.mark.parametrize("snapname,properties", [
    (None, ["user_prop=on", "otheruser_prop=on"]),
    (f"@pyzfscmds-test", ["user_prop=on", "otheruser_prop=on"]),
    ("", ["user_prop=on", "otheruser_prop=on"]),
    ("@", ["user_prop=on", "otheruser_prop=on"])
])
# Acceptable options
@pytest.mark.parametrize("recursive", [True, False])
@require_zpool
@require_test_dataset
def test_zfs_snapshot_name_fails(zpool, test_dataset, snapname, recursive, properties):
    with pytest.raises((TypeError, RuntimeError)):
        pyzfscmds.cmd.zfs_snapshot("/".join([zpool, test_dataset]), snapname,
                                   recursive=recursive, properties=properties)


# Incorrect options to test
@pytest.mark.parametrize("properties", [
    ["mountpoint"], ["mountpoint=legacy"], "mountpoint=legacy"
])
# Acceptable options
@pytest.mark.parametrize("recursive", [True, False])
@require_zpool
@require_test_dataset
def test_zfs_snapshot_property_fails(zpool, test_dataset, recursive, properties):
    snapname = f"@pyzfscmds-{datetime.datetime.now().isoformat()}"
    with pytest.raises(RuntimeError):
        pyzfscmds.cmd.zfs_snapshot("/".join([zpool, test_dataset]), snapname,
                                   recursive=recursive, properties=properties)


def test_zfs_snapshot_nonexistant_dataset_fails():
    with pytest.raises(RuntimeError):
        pyzfscmds.cmd.zfs_snapshot(
            "nonexistantdataset", f"@pyzfscmds-{datetime.datetime.now().isoformat()}")


@pytest.mark.parametrize("recursive", [True, False])
@pytest.mark.parametrize("properties", [None, [
    "pyzfscmds:user_prop=on", "pyzfscmds:otheruser_prop=on"]])
@require_zpool
@require_test_dataset
def test_zfs_snapshot_successful(zpool, test_dataset, recursive, properties):
    snapname = f"pyzfscmds-{datetime.datetime.now().isoformat()}"
    """ Test will pass if snapshot successful"""
    pyzfscmds.cmd.zfs_snapshot("/".join([zpool, test_dataset]), snapname,
                               recursive=recursive, properties=properties)
