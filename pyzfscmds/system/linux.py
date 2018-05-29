import re


def mountpoint_dataset(mountpoint: str):
    """
    Check if dataset is a 'zfs' mount.
    return dataset, or None if not found
    """

    target = re.compile(r'\b.*\s*' + mountpoint + r'\s*zfs\b')

    with open("/proc/mounts") as f:
        mount = next((ds for ds in f.read().splitlines() if target.search(ds)), None)

    return None if mount is None else mount.split()[0]


def dataset_mountpoint(dataset: str):
    """
    Get dataset mountpoint, or None if not found
    """

    target = re.compile(r'\b' + dataset + r'\s/.*\szfs\b')

    with open("/proc/mounts") as f:
        mount = next((ds for ds in f.read().splitlines() if target.search(ds)), None)

    if mount is None:
        return None

    split_match = mount.split()

    if split_match[3] == "zfs":
        # User used a mountpoint with spaces, zfs is at index 3
        mountpoint = " ".join([split_match[1], split_match[2]])
    else:
        # Space is in ASCII code, decode it
        if "\\" in split_match[1]:
            mountpoint = bytes(split_match[1], 'ascii').decode('unicode_escape')
        else:
            mountpoint = split_match[1]

    return mountpoint


def zfs_module_loaded():
    with open("/proc/modules") as f:
        if "zfs" not in f.read():
            return False

    return True
