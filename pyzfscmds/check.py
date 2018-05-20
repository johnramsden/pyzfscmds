"""
Startup checks
"""

import subprocess

import pyzfscmds.system.agnostic as zfssys


def is_root_on_zfs():
    """Check if running root on ZFS"""
    system = zfssys.check_valid_system()
    if system is None:
        raise RuntimeError(f"System is not yet supported by pyzfscmds\n")

    root_dataset = None
    if zfssys.zfs_module_loaded() and zpool_exists():
        root_dataset = zfssys.mountpoint_dataset("/")

    if root_dataset is None:
        raise RuntimeError("System is not booting off a ZFS root dataset\n")

    return True


def zpool_exists() -> bool:
    try:
        subprocess.check_call(["zpool", "get", "-H", "version"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return False

    return True
