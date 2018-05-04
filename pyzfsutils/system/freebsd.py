import subprocess
import re


def mountpoint_dataset(mountpoint):
    """
    Check if dataset at mountpoint is a 'zfs' mount.
    return dataset, or None if not found
    """
    mount = None
    try:
        mount = subprocess.check_output(
            ['mount'], universal_newlines=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to get mount data")

    mount_list = mount.splitlines()

    dataset = None
    target = re.compile(r'.*(?=\son\s' + mountpoint + '\stype\szfs\s)')
    for m in mount_list:
        res = target.match(m)
        if res:
            dataset = res.group()
            break

    return dataset


def zfs_module_loaded():
    try:
        subprocess.check_call(["sysctl", "vfs.zfs.version.spa"])
    except subprocess.CalledProcessError:
        return False

    return True
