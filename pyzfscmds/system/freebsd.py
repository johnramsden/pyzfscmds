import subprocess
import re


def _mount_list():
    try:
        mount = subprocess.check_output(
            ['mount'], universal_newlines=True, stderr=subprocess.PIPE)
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

    target = re.compile(r'.*(?=\son\s' + mountpoint + '\stype\szfs\s)')

    dataset_match = next(
        (target.match(ds) for ds in mount_list if target.match(ds)), None)

    return None if dataset_match is None else dataset_match.group()


def dataset_mountpoint(dataset: str):
    """
    Get dataset mountpoint, or None if not found
    """

    try:
        mount_list = _mount_list()
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to get mount data")

    target = re.compile(r'\b' + dataset + r'\s' + r'on\s/.*\szfs\b')

    mount = next((ds for ds in mount_list if target.search(ds)), None)

    return None if mount is None else mount.split(" ")[2]


def zfs_module_loaded():
    try:
        subprocess.check_call(["sysctl", "vfs.zfs.version.spa"])
    except subprocess.CalledProcessError:
        return False

    return True
