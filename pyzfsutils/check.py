"""
Startup checks
"""

import subprocess
import platform

import pyzfsutils.system.linux as zfslinux
import pyzfsutils.system.freebsd as zfsfreebsd


def is_root_on_zfs():
    system = check_valid_system()
    if system == 'linux' and zfslinux.zfs_module_loaded() and zpool_exists():
        root_dataset = zfslinux.mountpoint_dataset("/")
    elif system == 'freebsd' and zfsfreebsd.zfs_module_loaded() and zpool_exists():
        root_dataset = zfsfreebsd.mountpoint_dataset("/")
    else:
        raise RuntimeError(f"{system} is not yet supported by pyzfsutils\n")

    if root_dataset is None:
        raise RuntimeError("System is not booting off ZFS root dataset\n")

    return True


def check_valid_system():
    valid_platforms = ['linux', 'freebsd']
    system = platform.system().lower()
    if system in valid_platforms:
        return system
    return None


def zpool_exists() -> bool:
    try:
        subprocess.check_call(["zpool", "get", "-H", "version"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "No pool found, a zpool is required to use pyzfsutils.\n")

    return True
