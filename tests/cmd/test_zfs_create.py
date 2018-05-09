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


@pytest.mark.parametrize("properties", [None, [], ["compression=off"]])
@pytest.mark.parametrize("create_parent", [True, False])
# @pytest.mark.parametrize("mounted", [True, False])
@require_zpool
@require_test_dataset
def test_zfs_create_dataset_successful(zpool,
                                       test_dataset,
                                       properties,
                                       create_parent):
    # Cannot parameterize, must be unique
    dataset_name = "/".join([zpool,
                             test_dataset,
                             f"pyzfsutils-{datetime.datetime.now().isoformat()}"])
    print(f"Creating {dataset_name}")

    pyzfsutils.cmd.zfs_create_dataset(dataset_name,
                                      create_parent=create_parent,
                                      properties=properties)


@pytest.mark.parametrize("name", [f"@pyzfsutils-test", "", "@"])
@pytest.mark.parametrize("properties", [None, [], ["compression=off"]])
@pytest.mark.parametrize("create_parent", [True, False])
# @pytest.mark.parametrize("mounted", [True, False])
@require_zpool
@require_test_dataset
def test_zfs_create_dataset_fails(zpool,
                                  test_dataset,
                                  name,
                                  properties,
                                  create_parent):
    print(f"Creating {zpool}/{name}")

    with pytest.raises((TypeError, RuntimeError)):
        pyzfsutils.cmd.zfs_create_dataset(f"{zpool}/{test_dataset}/{name}",
                                          create_parent=create_parent,
                                          properties=properties)


@pytest.mark.parametrize("properties", [
    None, [], ["compression=off", "primarycache=none"]])
@pytest.mark.parametrize("create_parent", [True, False])
@pytest.mark.parametrize("sparse", [True, False])
@pytest.mark.parametrize("blocksize", [512, 4096])
@pytest.mark.parametrize("size", [512, 4096])
@require_zpool
@require_test_dataset
def test_zfs_create_zvol_successful(zpool,
                                    test_dataset,
                                    properties,
                                    create_parent,
                                    sparse,
                                    size,
                                    blocksize):
    # Cannot parameterize, must be unique
    volume_name = "/".join([zpool,
                            test_dataset,
                            f"pyzfsutils-{datetime.datetime.now().isoformat()}"])
    print(f"Creating {volume_name}")
    pyzfsutils.cmd.zfs_create_zvol(volume_name,
                                   size,
                                   blocksize=blocksize,
                                   sparse=sparse,
                                   size_suffix="K",
                                   create_parent=create_parent,
                                   properties=properties)


@pytest.mark.parametrize("name", [f"@pyzfsutils-test", "", "@"])
@pytest.mark.parametrize("properties", [
    None, [], ["compression=off", "primarycache=none"]])
@pytest.mark.parametrize("create_parent", [True, False])
@pytest.mark.parametrize("sparse", [True, False])
@pytest.mark.parametrize("blocksize", [512, 4096])
@pytest.mark.parametrize("size", [512, 4096])
@require_zpool
@require_test_dataset
def test_zfs_create_zvol_fails(zpool,
                               test_dataset,
                               name,
                               properties,
                               create_parent,
                               sparse,
                               size,
                               blocksize):
    print(f"Creating {zpool}/{test_dataset}/{name}")

    with pytest.raises((TypeError, RuntimeError)):
        pyzfsutils.cmd.zfs_create_zvol(f"{zpool}/{test_dataset}/{name}",
                                       size,
                                       blocksize=blocksize,
                                       sparse=sparse,
                                       size_suffix="K",
                                       create_parent=create_parent,
                                       properties=properties)


@pytest.mark.parametrize("properties", [
    None, [], ["compression=off", "primarycache=none"]])
@pytest.mark.parametrize("create_parent", [True, False])
@pytest.mark.parametrize("sparse", [True, False])
@pytest.mark.parametrize("blocksize", [512, 4096])
@pytest.mark.parametrize("size", [0, -5])
@require_zpool
@require_test_dataset
def test_zfs_create_zvol_fails_size(zpool,
                                    test_dataset,
                                    properties,
                                    create_parent,
                                    sparse,
                                    size,
                                    blocksize):
    """ Test will pass if create fails"""

    volume_name = "/".join([zpool,
                            test_dataset,
                            f"pyzfsutils-{datetime.datetime.now().isoformat()}"])
    print(f"Creating {volume_name}")

    with pytest.raises((TypeError, RuntimeError)):
        pyzfsutils.cmd.zfs_create_zvol(volume_name,
                                       size,
                                       blocksize=blocksize,
                                       sparse=sparse,
                                       size_suffix="K",
                                       create_parent=create_parent,
                                       properties=properties)
