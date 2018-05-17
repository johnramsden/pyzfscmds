import os

import pytest

import pyzfscmds.cmd

# Check for skip environment variable, to skip set TEST_ZFS_*="false"
module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


@pytest.mark.parametrize("recursive", [True, False])
@pytest.mark.parametrize("depth", [None, 0, 1])
@pytest.mark.parametrize("scripting", [True, False])
@pytest.mark.parametrize("parsable", [True, False])
@pytest.mark.parametrize("columns", [
    None, ["name"], ["name", "property", "value", "received", "source"],
    # ["name"], ["property"], ["value"], ["received"], ["source"],
    # ["name", "property", "value", "source"]
])
@pytest.mark.parametrize("zfs_types", [
    None, [], ["all"], ["filesystem", "snapshot"]
    # ["filesystem"], ["snapshot"], ["volume"]
])
@pytest.mark.parametrize("source", [
    None, [], ["local"],
    ["local", "default", "inherited", "temporary", "received", "none"],
    # ["default"], ["inherited"], ["temporary"], ["received"], ["none"]
])
@pytest.mark.parametrize("properties", [
    None, ["all"], ["mountpoint", "canmount"]
])
@require_zpool
@require_test_dataset
def test_zfs_get_successful(zpool, test_dataset, recursive, depth, scripting,
                            parsable, columns, zfs_types, source, properties):
    """ Test will pass if get successful"""
    pyzfscmds.cmd.zfs_get("/".join([zpool, test_dataset]),
                          recursive=recursive,
                          depth=depth,
                          scripting=scripting,
                          parsable=parsable,
                          columns=columns,
                          zfs_types=zfs_types,
                          source=source,
                          properties=properties)


# Incorrect options to test
@pytest.mark.parametrize(
    "columns,zfs_types,source,properties", [
        # Test incorrect columns
        (["fakecolumn"], ["all"], ["local"], ["all"]),
        (["fakecolumnone", "fakecolumntwo"], ["all"], ["local"], ["all"]),
        ("notalist", ["all"], ["local"], ["all"]),
        # Test incorrect zfs_types
        (["name"], ["notatype"], ["local"], ["all"]),
        (["name"], "notalist", ["local"], ["all"]),
        # Test incorrect source
        (["name"], ["all"], ["notasource"], ["all"]),
        (["name"], ["all"], "notalist", ["all"]),
        # Test incorrect properties
        (["name"], ["all"], ["local"], ["notaprop"]),
        (["name"], ["all"], ["local"], "notalist"),
    ])
# Acceptable options
@pytest.mark.parametrize("recursive", [True, False])
@pytest.mark.parametrize("depth", [None, 0, 1])
@pytest.mark.parametrize("scripting", [True, False])
@pytest.mark.parametrize("parsable", [True, False])
@require_zpool
@require_test_dataset
def test_zfs_get_fails(zpool, test_dataset, recursive, depth, scripting,
                       parsable, columns, zfs_types, source, properties):
    with pytest.raises(RuntimeError):
        pyzfscmds.cmd.zfs_get("/".join([zpool, test_dataset]),
                              recursive=recursive,
                              depth=depth,
                              scripting=scripting,
                              parsable=parsable,
                              columns=columns,
                              zfs_types=zfs_types,
                              source=source,
                              properties=properties)
