import pyzfscmds.check

system = pyzfscmds.check.check_valid_system()

if system == "linux":
    import pyzfscmds.system.linux
    mountpoint_dataset = pyzfscmds.system.linux.mountpoint_dataset
    zfs_module_loaded = pyzfscmds.system.linux.zfs_module_loaded
    dataset_mountpoint = pyzfscmds.system.linux.dataset_mountpoint
elif system == "freebsd":
    import pyzfscmds.system.freebsd
    mountpoint_dataset = pyzfscmds.system.freebsd.mountpoint_dataset
    zfs_module_loaded = pyzfscmds.system.freebsd.zfs_module_loaded
    dataset_mountpoint = pyzfscmds.system.freebsd.dataset_mountpoint
else:
    raise SystemError("System not supported by pyzfscmds")
