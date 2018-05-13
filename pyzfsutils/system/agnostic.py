import pyzfsutils.check

system = pyzfsutils.check.check_valid_system()

if system == "linux":
    import pyzfsutils.system.linux
    mountpoint_dataset = pyzfsutils.system.linux.mountpoint_dataset
    zfs_module_loaded = pyzfsutils.system.linux.zfs_module_loaded
    dataset_mountpoint = pyzfsutils.system.linux.dataset_mountpoint
elif system == "freebsd":
    import pyzfsutils.system.freebsd
    mountpoint_dataset = pyzfsutils.system.freebsd.mountpoint_dataset
    zfs_module_loaded = pyzfsutils.system.freebsd.zfs_module_loaded
    dataset_mountpoint = pyzfsutils.system.freebsd.dataset_mountpoint
else:
    raise SystemError("System not supported by pyzfsutils")
