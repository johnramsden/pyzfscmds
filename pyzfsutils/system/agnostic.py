import pyzfsutils.check

system = pyzfsutils.check.check_valid_system()

if system == "linux":
    import pyzfsutils.system.linux
    mountpoint_dataset = pyzfsutils.system.linux.mountpoint_dataset
    zfs_module_loaded = pyzfsutils.system.linux.zfs_module_loaded
elif system == "freebsd":
    import pyzfsutils.system.freebsd
    mountpoint_dataset = pyzfsutils.system.freebsd.mountpoint_dataset
    zfs_module_loaded = pyzfsutils.system.freebsd.zfs_module_loaded
else:
    raise SystemError("System not supported by pyzfsutils")
