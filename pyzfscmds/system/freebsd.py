import subprocess
import re


def _mount_list():
    try:
        mount = subprocess.check_output(
            ['mount', '-p'], universal_newlines=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise

    return mount.splitlines()


def mountpoint_dataset(mountpoint: str):
    """
    Check if dataset at mountpoint is a 'zfs' mount.
    return dataset, or None if not found
    """
    try:
        mount_list = _mount_list()
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to get mount data")

    target = re.compile(r'\b\w+\s+' + mountpoint + r'\s+zfs\b')

    dataset = next((ds for ds in mount_list if target.search(ds)), None)

    return dataset.split()[0] if dataset is not None else None


def dataset_mountpoint(dataset: str):
    """
    Get dataset mountpoint, or None if not found
    """

    try:
        mount_list = _mount_list()
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to get mount data")

    target = re.compile(r'\b' + dataset + r'\s+/.*\s+zfs\b')

    mount = next((ds for ds in mount_list if target.search(ds)), None)

    if mount is None:
        return None

    split_match = mount.split()

    if split_match[3] == "zfs":
        # User used a mountpoint with spaces, zfs is at index 3
        mp = " ".join([split_match[1], split_match[2]])
    else:
        mp = split_match[1]

    return mp


def zfs_module_loaded():
    try:
        subprocess.check_call(["sysctl", "vfs.zfs.version.spa"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return False

    return True
