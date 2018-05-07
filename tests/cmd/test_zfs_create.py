import datetime

import pytest

import pyzfsutils.cmd

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool


@pytest.mark.parametrize("properties", [None, [], ["compression=off"]])
@pytest.mark.parametrize("create_parent", [True, False])
@pytest.mark.parametrize("mounted", [True, False])
@require_zpool
def test_zfs_create_dataset_successful(zpool,
                                       properties,
                                       create_parent,
                                       mounted):
    # Cannot parameterize, must be unique
    dataset_name = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    print(f"Creating {zpool}/{dataset_name}")
    """ Test will pass if clone successful"""
    pyzfsutils.cmd.zfs_create_dataset(f"{zpool}/{dataset_name}",
                                      create_parent=create_parent,
                                      properties=properties)


@pytest.mark.parametrize("name", [f"@pyzfsutils-test", "", "@"])
@pytest.mark.parametrize("properties", [None, [], ["compression=off"]])
@pytest.mark.parametrize("create_parent", [True, False])
@pytest.mark.parametrize("mounted", [True, False])
@require_zpool
def test_zfs_create_dataset_fails(zpool,
                                  name,
                                  properties,
                                  create_parent,
                                  mounted):
    print(f"Creating {zpool}/{name}")
    """ Test will pass if clone fails"""

    with pytest.raises((TypeError, RuntimeError)):
        pyzfsutils.cmd.zfs_create_dataset(f"{zpool}/{name}",
                                          create_parent=create_parent,
                                          properties=properties)


@pytest.mark.parametrize("properties", [
    None, [], ["compression=off", "primarycache=none"]])
@pytest.mark.parametrize("create_parent", [True, False])
@pytest.mark.parametrize("sparse", [True, False])
@pytest.mark.parametrize("blocksize", [512, 4096])
@pytest.mark.parametrize("size", [512, 4096])
@require_zpool
def test_zfs_create_zvol_successful(zpool,
                                    properties,
                                    create_parent,
                                    sparse,
                                    size,
                                    blocksize):
    # Cannot parameterize, must be unique
    volume_name = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    print(f"Creating {zpool}/{volume_name}")
    """ Test will pass if create successful"""
    pyzfsutils.cmd.zfs_create_zvol(f"{zpool}/{volume_name}",
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
def test_zfs_create_zvol_fails(zpool,
                               name,
                               properties,
                               create_parent,
                               sparse,
                               size,
                               blocksize):
    print(f"Creating {zpool}/{name}")
    """ Test will pass if create fails"""

    with pytest.raises((TypeError, RuntimeError)):
        pyzfsutils.cmd.zfs_create_zvol(f"{zpool}/{name}",
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
def test_zfs_create_zvol_fails_size(zpool,
                                    properties,
                                    create_parent,
                                    sparse,
                                    size,
                                    blocksize):
    """ Test will pass if create fails"""

    volume_name = f"pyzfsutils-{datetime.datetime.now().isoformat()}"
    print(f"Creating {zpool}/{volume_name}")

    with pytest.raises((TypeError, RuntimeError)):
        pyzfsutils.cmd.zfs_create_zvol(f"{zpool}/{volume_name}",
                                       size,
                                       blocksize=blocksize,
                                       sparse=sparse,
                                       size_suffix="K",
                                       create_parent=create_parent,
                                       properties=properties)
