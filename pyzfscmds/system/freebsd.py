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

    no_tabs = re.compile(r'[^\t]+')

    # Remove tabs from mount output leaving list of items
    mount_line_list = [no_tabs.findall(l) for l in mount_list]

    # Find first dataset match on mountpoint
    return next(
        (ds[0] for ds in mount_line_list if ds[2] == 'zfs' and ds[1] == mountpoint), None)


def dataset_mountpoint(dataset: str):
    """
    Get dataset mountpoint, or None if not found
    """

    try:
        mount_list = _mount_list()
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to get mount data")

    no_tabs = re.compile(r'[^\t]+')

    # Remove tabs from mount output leaving list of items
    mount_line_list = [no_tabs.findall(l) for l in mount_list]

    # Find first match on dataset
    return next((ds[1] for ds in mount_line_list if ds[2] == 'zfs' and ds[0] == dataset), None)


def zfs_module_loaded():
    try:
        subprocess.check_call(["sysctl", "vfs.zfs.version.spa"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return False

    return True
