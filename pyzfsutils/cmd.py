"""ZFS library"""

import itertools
import subprocess

from typing import List

import pyzfsutils.check
import pyzfsutils.utility
import pyzfsutils.system.agnostic

"""
ZFS commands
"""


class _Command:

    def __init__(self,
                 sub_command: str,
                 options: list = None,
                 properties: List[str] = None,
                 targets: List[str] = None,
                 main_command: str = "zfs"):
        self.main_command = main_command
        self.sub_command = sub_command
        self.targets = targets

        self.call_args = [o for o in options] if options is not None else []

        if properties:
            self.properties = self._prepare_properties(properties)

    @staticmethod
    def _prepare_properties(properties: List[str]) -> list:
        if properties is not None:
            prop_list = [["-o", prop] for prop in properties]
            return list(itertools.chain.from_iterable(prop_list))
        return []

    def argcheck_depth(self, depth):
        if depth is not None:
            if depth < 0:
                raise RuntimeError("Depth cannot be negative")
            self.call_args.extend(["-d", str(depth)])

    def argcheck_columns(self, columns: list):
        if columns:
            if "all" in columns:
                self.call_args.extend(["-o", "all"])
            else:
                self.call_args.extend(["-o", ",".join(columns)])

    def run(self) -> str:

        arguments = self.call_args

        if hasattr(self, 'properties') and self.properties:
            arguments.extend(self.properties)

        if hasattr(self, 'targets') and self.targets:
            arguments.extend(self.targets)

        zfs_call = [self.main_command, self.sub_command] + arguments

        try:
            output = subprocess.check_output(zfs_call,
                                             universal_newlines=True,
                                             stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise e

        return output


"""
zpool Commands
"""


def zpool_set(pool: str, prop: str) -> str:
    """
    zpool set property=value pool

             Sets the given property on the specified pool.  See the
             Properties section for more information on what properties
             can be set and acceptable values.
    """
    if pool is None:
        raise TypeError("Target name cannot be of type 'None'")

    command = _Command("set", [],
                       main_command="zpool",
                       targets=[prop, pool])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to set pool property {prop}\n{e.output}\n")


def zpool_get(pool: str = None,
              scripting: bool = True,
              properties: list = None,
              columns: list = None,
              parsable: bool = False) -> str:
    """
     zpool get [-Hp] [-o field[,field]...] all|property[,property]...
             pool...
             Retrieves the given list of properties (or all properties if
             all is used) for the specified storage pool(s).  These prop‐
             erties are displayed with the following fields:

                     name          Name of storage pool
                     property      Property name
                     value         Property value
                     source        Property source, either 'default' or 'local'.

             See the Properties section for more information on the avail‐
             able pool properties.

             -H      Scripted mode.  Do not display headers, and separate
                     fields by a single tab instead of arbitrary space.

             -o field
                     A comma-separated list of columns to display.
                     name,property,value,source is the default value.

             -p      Display numbers in parsable (exact) values.
    """
    call_args = []

    if scripting:
        call_args.append("-H")

    if parsable:
        call_args.append("-p")

    if properties is None:
        property_target = "all"
    elif properties:
        if "all" in properties:
            if len(properties) < 2:
                property_target = "all"
            else:
                raise RuntimeError(f"Cannot use 'all' with other properties")
        else:
            property_target = ",".join(properties)
    else:
        raise RuntimeError(f"Cannot request no property type")

    target_list = [property_target]
    if pool is not None:
        target_list.append(pool)

    command = _Command("get", call_args,
                       main_command="zpool",
                       targets=target_list)

    command.argcheck_columns(columns)

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get zfs property '{property_target}' "
                           f"from {pool}\n{e.output}\n")


"""
zfs Commands
"""


def zfs_create_dataset(filesystem: str,
                       create_parent: bool = False,
                       mounted: bool = True,
                       properties: list = None) -> str:
    """
     zfs create	[-pu] [-o property=value]... filesystem
    """
    if filesystem is None:
        raise TypeError("Filesystem name cannot be of type 'None'")

    call_args = []

    if create_parent:
        call_args.append('-p')

    if not mounted:
        if pyzfsutils.check.check_valid_system() == "freebsd":
            call_args.append('-u')
        else:
            raise SystemError("-u is not valid on this system")

    create = _Command("create", call_args, properties=properties, targets=[filesystem])

    try:
        return create.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create {filesystem}\n{e.output}\n")


def zfs_create_zvol(volume: str,
                    size: int,
                    size_suffix: str = "G",
                    blocksize: int = None,
                    create_parent: bool = False,
                    sparse: bool = False,
                    properties: list = None) -> str:
    """
     zfs create	[-ps] [-b blocksize] [-o property=value]... -V size volume
    """
    if volume is None:
        raise TypeError("Filesystem name cannot be of type 'None'")

    call_args = []

    if create_parent:
        call_args = ["-p"]

    if sparse:
        call_args.append('-s')

    if blocksize:
        call_args.extend(['-b', str(blocksize)])

    call_args.extend(['-V', f"{str(size)}{size_suffix}"])

    command = _Command("create", call_args, properties=properties, targets=[volume])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create {volume}\n{e.output}\n")


def zfs_clone(snapname: str,
              filesystem: str,
              properties: list = None,
              create_parent: bool = False) -> str:

    if snapname is None:
        raise TypeError("Snapshot name cannot be of type 'None'")

    call_args = []

    if create_parent:
        call_args = ["-p"]

    command = _Command("clone", call_args, properties=properties, targets=[snapname, filesystem])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to clone {filesystem}\n{e.output}\n")


def zfs_snapshot(filesystem: str,
                 snapname: str,
                 recursive: bool = False,
                 properties: list = None) -> str:
    """
     zfs snapshot|snap [-r] [-o	property=value]...
     filesystem@snapname|volume@snapname
     filesystem@snapname|volume@snapname...
    """
    if snapname is None:
        raise TypeError("Snapshot name cannot be of type 'None'")

    call_args = []

    if recursive:
        call_args = ["-r"]

    command = _Command("snapshot", call_args,
                       properties=properties, targets=[f"{filesystem}@{snapname}"])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to snapshot {filesystem}\n{e.output}\n")


def zfs_get(target: str,
            recursive: bool = False,
            depth: int = None,
            scripting: bool = True,
            parsable: bool = False,
            columns: list = None,
            zfs_types: list = None,
            source: list = None,
            properties: list = None) -> str:
    """
     zfs get [-r|-d depth] [-Hp] [-o all | field[,field]...] [-t
     type[,type]...] [-s source[,source]...] all | property[,property]...
     filesystem|volume|snapshot...
    """

    call_args = []

    if recursive:
        call_args.append("-r")

    if scripting:
        call_args.append("-H")

    if parsable:
        call_args.append("-p")

    if zfs_types:
        call_args.extend(["-t", ",".join(zfs_types)])

    if source:
        call_args.extend(["-s", ",".join(source)])

    if properties is None:
        property_target = "all"
    elif properties:
        if "all" in properties:
            if len(properties) < 2:
                property_target = "all"
            else:
                raise RuntimeError(f"Cannot use 'all' with other properties")
        else:
            property_target = ",".join(properties)
    else:
        raise RuntimeError(f"Cannot request no property type")

    command = _Command("get", call_args, targets=[property_target, target])

    command.argcheck_depth(depth)
    command.argcheck_columns(columns)

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get zfs properties of {target}\n{e.output}\n")


def zfs_list(target: str,
             recursive: bool = False,
             depth: int = None,
             scripting: bool = True,
             parsable: bool = False,
             columns: list = None,
             zfs_types: list = None,
             sort_properties_ascending: list = None,
             sort_properties_descending: list = None) -> str:
    """
     zfs list [-r|-d depth] [-Hp] [-o property[,property]...] [-t
     type[,type]...] [-s property]... [-S property]...
     filesystem|volume|snapshot...
    """

    call_args = []

    if recursive:
        call_args.append("-r")

    if scripting:
        call_args.append("-H")

    if parsable:
        call_args.append("-p")

    if zfs_types:
        call_args.extend(["-t", ",".join(zfs_types)])

    if sort_properties_ascending is not None:
        call_args.extend(
            [p for prop in sort_properties_ascending for p in ("-s", prop)])

    if sort_properties_descending is not None:
        call_args.extend(
            [p for prop in sort_properties_descending for p in ("-S", prop)])

    command = _Command("list", call_args, targets=[target])
    command.argcheck_depth(depth)
    command.argcheck_columns(columns)

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get zfs list of {target}\n{e.output}\n")


def zfs_destroy(target: str,
                recursive_children: bool = False,
                recursive_dependents: bool = False,
                force_unmount: bool = False,
                dry_run: bool = False,
                machine_parsable: bool = False,
                verbose: bool = False) -> str:
    """
    zfs destroy [-fnpRrv] filesystem|volume
    """
    if target is None:
        raise TypeError("Target name cannot be of type 'None'")

    call_args = []

    if recursive_children:
        call_args.append("-r")
    if recursive_dependents:
        call_args.append("-R")
    if force_unmount:
        call_args.append("-f")
    if dry_run:
        call_args.append("-n")
    if machine_parsable:
        call_args.append("-p")
    if verbose:
        call_args.append("-v")

    command = _Command("destroy", call_args, targets=[target])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to destroy {target}\n{e.output}\n")


def zfs_destroy_snapshot(snapname: str,
                         recursive_descendents: bool = False,
                         recursive_clones: bool = False,
                         dry_run: bool = False,
                         machine_parsable: bool = False,
                         verbose: bool = False,
                         defer: bool = False) -> str:
    """
     zfs destroy [-dnpRrv] snapshot[%snapname][,...]
    """
    if snapname is None:
        raise TypeError("Snapshot name cannot be of type 'None'")

    call_args = []

    if recursive_descendents:
        call_args.append("-r")
    if recursive_clones:
        call_args.append("-R")
    if dry_run:
        call_args.append("-n")
    if machine_parsable:
        call_args.append("-p")
    if verbose:
        call_args.append("-v")
    if defer:
        call_args.append("-d")

    command = _Command("destroy", call_args, targets=[snapname])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to destroy {snapname}\n{e.output}\n")


def zfs_rollback(snapname: str,
                 destroy_between: bool = False,
                 destroy_more_recent: bool = False,
                 force_unmount: bool = False):
    """
     zfs rollback [-rRf] snapshot
    """
    if snapname is None:
        raise TypeError("Snapshot name cannot be of type 'None'")

    call_args = []

    if destroy_between:
        call_args.append("-r")
    if destroy_more_recent:
        call_args.append("-R")
    if force_unmount:
        call_args.append("-f")

    command = _Command("rollback", call_args, targets=[snapname])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to rollback {snapname}\n{e.output}\n")


def zfs_promote(clone: str) -> str:
    """
     zfs promote clone-filesystem
    """
    command = _Command("promote", [], targets=[clone])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to promote {clone}\n{e.output}\n")


def zfs_rename(target_source: str,
               target_dest: str,
               create_parents: bool = False,
               dont_remount: bool = False,
               force_unmount: bool = False,
               recursive: bool = False) -> str:
    """
     zfs rename	[-f] filesystem|volume|snapshot	filesystem|volume|snapshot

     zfs rename	[-f] -p	filesystem|volume filesystem|volume

     zfs rename	-u [-p]	filesystem filesystem

     zfs rename	-r snapshot snapshot
    """
    if target_source is None or target_dest is None:
        raise TypeError("Target name cannot be of type 'None'")

    call_args = []

    if create_parents:
        call_args.append("-p")

    if dont_remount:
        call_args.append("-u")

    if force_unmount:
        call_args.append("-f")

    if recursive:
        call_args.append("-r")

    command = _Command("rename", call_args, targets=[target_source, target_dest])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to rename {target_source} to {target_dest}\n{e.output}\n")


def zfs_set(target: str, prop: str) -> str:
    """
     zfs set property=value [property=value]...	filesystem|volume|snapshot
    """
    if target is None:
        raise TypeError("Target name cannot be of type 'None'")

    command = _Command("set", [], targets=[prop, target])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to \n{e.output}\n")


def zfs_inherit(prop: str,
                target: str,
                recursive: bool = False,
                revert: bool = False) -> str:
    """
     zfs inherit [-rS] property	filesystem|volume|snapshot...
    """
    if prop is None:
        raise TypeError("Property name cannot be of type 'None'")

    if target is None:
        raise TypeError("Target name cannot be of type 'None'")

    call_args = []

    if recursive:
        call_args.append("-r")

    if revert:
        call_args.append("-S")

    command = _Command("inherit", call_args, targets=[prop, target])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to inherit property\n{e.output}\n")


def zfs_upgrade_list(supported: bool = False) -> str:
    """
     zfs upgrade [-v]

     Displays a list of file systems that are not the most recent version.

     -v	 Displays ZFS filesystem versions supported by the current
         software. The current ZFS filesystem version and all previous
         supported versions are	displayed, along with an explanation
         of the	features provided with each version.
     """
    call_args = []
    if supported:
        call_args.append("-v")

    command = _Command("upgrade", call_args)

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to list upgradeable filesystems\n{e.output}\n")


def zfs_upgrade(target: str = None,
                descendent: bool = False,
                version: str = None,
                upgrade_all: bool = False) -> str:
    """
    zfs upgrade [-r] [-V version] -a |	filesystem
    """
    if target is not None and upgrade_all:
        raise RuntimeError("Both target and upgrade all cannot be true")

    call_args = []

    if descendent:
        call_args.append("-r")

    if upgrade_all:
        call_args.append("-a")

    if version is not None:
        call_args.extend(["-V", version])

    targets = [target] if target is not None else []

    command = _Command("upgrade", call_args, targets=targets)

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to run upgrade\n{e.output}\n")


def zfs_mount_list() -> str:
    """
     zfs mount

     Displays all ZFS file systems currently mounted.
     """

    command = _Command("mount", [])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to \n{e.output}\n")


def zfs_mount(target: str = None,
              progress: bool = False,
              overlay: bool = False,
              properties: list = None,
              mount_all: bool = False) -> str:
    """

     zfs mount [-vO] [-o property[,property]...] -a | filesystem
    """
    if target is not None and mount_all:
        raise RuntimeError("Both target and unmount all cannot be true")

    call_args = []

    if progress:
        call_args.append("-v")

    if overlay:
        call_args.append("-O")

    if mount_all:
        call_args.append("-a")

    if properties:
        call_args.extend(["-o", ",".join(properties)])

    targets = [target] if target is not None else []

    command = _Command("mount", call_args, targets=targets)

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to mount target\n{e.output}\n")


def zfs_unmount(target: str = None,
                force: bool = False,
                unmount_all: bool = False) -> str:
    """
     zfs unmount|umount	[-f] -a	| filesystem|mountpoint
    """
    if target is not None and unmount_all:
        raise RuntimeError("Both target and unmount all cannot be true")

    call_args = []

    if force:
        call_args.append("-f")

    if unmount_all:
        call_args.append("-a")

    targets = [target] if target is not None else []

    command = _Command("unmount", call_args, targets=targets)

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to unmount {target}\n{e.output}\n")

# TODO: Unimplemented:
# def zfs_userspace():
#     """
#      zfs userspace [-Hinp] [-o field[,field]...] [-s field]... [-S field]...
#      [-t type[,type]...] filesystem|snapshot
#
#      Displays space	consumed by, and quotas	on, each user in the specified
#      filesystem or snapshot. This corresponds to the userused@user and
#      userquota@user	properties.
#
#      -n	 Print numeric ID instead of user/group	name.
#
#      -H	 Do not	print headers, use tab-delimited output.
#
#      -p	 Use exact (parsable) numeric output.
#
#      -o field[,field]...
#          Display only the specified fields from	the following set:
#          type,name,used,quota.	The default is to display all fields.
#
#      -s field
#          Sort output by	this field. The	-s and -S flags	may be speci-
#          fied multiple times to	sort first by one field, then by
#          another. The default is -s type -s name.
#
#      -S field
#          Sort by this field in reverse order. See -s.
#
#      -t type[,type]...
#          Print only the	specified types	from the following set:
#          all,posixuser,smbuser,posixgroup,smbgroup.
#
#          The default is	-t posixuser,smbuser.
#
#          The default can be changed to include group types.
#
#      -i	 Translate SID to POSIX	ID. This flag currently	has no effect
#          on FreeBSD.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_groupspace():
#     """
#      zfs groupspace [-Hinp] [-o	field[,field]...] [-s field]...	[-S field]...
#      [-t type[,type]...] filesystem|snapshot
#
#      Displays space	consumed by, and quotas	on, each group in the speci-
#      fied filesystem or snapshot. This subcommand is identical to "zfs
#      userspace", except that the default types to display are -t
#      posixgroup,smbgroup.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
#
#
# def zfs_share():
#     """
#      zfs share -a | filesystem
#
#      Shares	ZFS file systems that have the sharenfs	property set.
#
#      -a	 Share all ZFS file systems that have the sharenfs property
#          set.  This command may	be executed on FreeBSD system startup
#          by /etc/rc.d/zfs.  For	more information, see variable
#          zfs_enable in rc.conf(5).
#
#      filesystem
#          Share the specified filesystem	according to the sharenfs
#          property. File	systems	are shared when	the sharenfs property
#          is set.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_unshare():
#     """
#    zfs unshare -a | filesystem|mountpoint
#
#      Unshares ZFS file systems that	have the sharenfs property set.
#
#      -a	 Unshares ZFS file systems that	have the sharenfs property
#          set.  This command may	be executed on FreeBSD system shutdown
#          by /etc/rc.d/zfs.  For	more information, see variable
#          zfs_enable in rc.conf(5).
#
#      filesystem | mountpoint
#          Unshare the specified filesystem. The command can also	be
#          given a path to a ZFS file system shared on the system.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_bookmark():
#     """
#      zfs bookmark snapshot bookmark
#
#      Creates a bookmark of the given snapshot.  Bookmarks mark the point
#      in time when the snapshot was created,	and can	be used	as the incre-
#      mental	source for a "zfs send"	command.
#
#      This feature must be enabled to be used.  See zpool-features(7) for
#      details on ZFS	feature	flags and the bookmark feature.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_send():
#     """
#      zfs send [-DnPpRveL] [-i snapshot | -I snapshot] snapshot
#
#      Creates a stream representation of the	last snapshot argument (not
#      part of -i or -I) which is written to standard	output.	The output can
#      be redirected to a file or to a different system (for example,	using
#      ssh(1)).  By default, a full stream is	generated.
#
#      -i snapshot
#          Generate an incremental stream	from the first snapshot	(the
#          incremental source) to	the second snapshot (the incremental
#          target).  The incremental source can be specified as the last
#          component of the snapshot name	(the @ character and
#          following) and	it is assumed to be from the same file system
#          as the	incremental target.
#
#          If the	destination is a clone,	the source may be the origin
#          snapshot, which must be fully specified (for example,
#          pool/fs@origin, not just @origin).
#
#      -I snapshot
#          Generate a stream package that	sends all intermediary snap-
#          shots from the	first snapshot to the second snapshot.	For
#          example, -I @a	fs@d is	similar	to -i @a fs@b; -i @b fs@c; -i
#          @c fs@d.  The incremental source may be specified as with the
#          -i option.
#
#      -R	 Generate a replication	stream package,	which will replicate
#          the specified filesystem, and all descendent file systems, up
#          to the	named snapshot.	When received, all properties, snap-
#          shots,	descendent file	systems, and clones are	preserved.
#
#          If the	-i or -I flags are used	in conjunction with the	-R
#          flag, an incremental replication stream is generated. The
#          current values	of properties, and current snapshot and	file
#          system	names are set when the stream is received. If the -F
#          flag is specified when	this stream is received, snapshots and
#          file systems that do not exist	on the sending side are
#          destroyed.
#
#      -D	 Generate a deduplicated stream. Blocks	which would have been
#          sent multiple times in	the send stream	will only be sent
#          once.	The receiving system must also support this feature to
#          receive a deduplicated	stream.	 This flag can be used regard-
#          less of the dataset's dedup property, but performance will be
#          much better if	the filesystem uses a dedup-capable checksum
#          (eg.  sha256).
#
#      -L	 Generate a stream which may contain blocks larger than	128KB.
#          This flag has no effect if the	large_blocks pool feature is
#          disabled, or if the recordsize	property of this filesystem
#          has never been	set above 128KB.  The receiving	system must
#          have the large_blocks pool feature enabled as well.  See
#          zpool-features(7) for details on ZFS feature flags and	the
#          large_blocks feature.
#
#      -e	 Generate a more compact stream	by using WRITE_EMBEDDED
#          records for blocks which are stored more compactly on disk by
#          the embedded_data pool	feature.  This flag has	no effect if
#          the embedded_data feature is disabled.	 The receiving system
#          must have the embedded_data feature enabled.  If the
#          lz4_compress feature is active	on the sending system, then
#          the receiving system must have	that feature enabled as	well.
#          See zpool-features(7) for details on ZFS feature flags	and
#          the embedded_data feature.
#
#      -p	 Include the dataset's properties in the stream. This flag is
#          implicit when -R is specified.	The receiving system must also
#          support this feature.
#
#      -n	 Do a dry-run ("No-op")	send.  Do not generate any actual send
#          data.	This is	useful in conjunction with the -v or -P	flags
#          to determine what data	will be	sent.  In this case, the ver-
#          bose output will be written to	standard output	(contrast with
#          a non-dry-run,	where the stream is written to standard	output
#          and the verbose output	goes to	standard error).
#
#      -P	 Print machine-parsable	verbose	information about the stream
#          package generated.
#
#      -v	 Print verbose information about the stream package generated.
#          This information includes a per-second	report of how much
#          data has been sent.
#
#      The format of the stream is committed.	You will be able to receive
#      your streams on future	versions of ZFS.
#
#      zfs send [-eL] [-i	snapshot|bookmark] filesystem|volume|snapshot
#
#      Generate a send stream, which may be of a filesystem, and may be
#      incremental from a bookmark.  If the destination is a filesystem or
#      volume, the pool must be read-only, or	the filesystem must not	be
#      mounted.  When	the stream generated from a filesystem or volume is
#      received, the default snapshot	name will be (--head--).
#
#      -i snapshot|bookmark
#          Generate an incremental send stream.  The incremental source
#          must be an earlier snapshot in	the destination's history.  It
#          will commonly be an earlier snapshot in the destination's
#          filesystem, in	which case it can be specified as the last
#          component of the name (the # or @ character and following).
#
#          If the	incremental target is a	clone, the incremental source
#          can be	the origin snapshot, or	an earlier snapshot in the
#          origin's filesystem, or the origin's origin, etc.
#
#      -L	 Generate a stream which may contain blocks larger than	128KB.
#          This flag has no effect if the	large_blocks pool feature is
#          disabled, or if the recordsize	property of this filesystem
#          has never been	set above 128KB.  The receiving	system must
#          have the large_blocks pool feature enabled as well.  See
#          zpool-features(7) for details on ZFS feature flags and	the
#          large_blocks feature.
#
#      -e	 Generate a more compact stream	by using WRITE_EMBEDDED
#          records for blocks which are stored more compactly on disk by
#          the embedded_data pool	feature.  This flag has	no effect if
#          the embedded_data feature is disabled.	 The receiving system
#          must have the embedded_data feature enabled.  If the
#          lz4_compress feature is active	on the sending system, then
#          the receiving system must have	that feature enabled as	well.
#          See zpool-features(7) for details on ZFS feature flags	and
#          the embedded_data feature.
#
#      zfs send [-Penv] -t receive_resume_token
#      Creates a send	stream which resumes an	interrupted receive.  The
#      receive_resume_token is the value of this property on the filesystem
#      or volume that	was being received into.  See the documentation	for
#      zfs receive -s	for more details.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_receive():
#     """
#      zfs receive|recv [-vnsFu] [-o origin=snapshot] filesystem|volume|snapshot
#
#      zfs receive|recv [-vnsFu] [-d | -e] [-o origin=snapshot] filesystem
#
#      Creates a snapshot whose contents are as specified in the stream pro-
#      vided on standard input. If a full stream is received,	then a new
#      file system is	created	as well. Streams are created using the "zfs
#      send" subcommand, which by default creates a full stream.  "zfs recv"
#      can be	used as	an alias for "zfs receive".
#
#      If an incremental stream is received, then the	destination file sys-
#      tem must already exist, and its most recent snapshot must match the
#      incremental stream's source. For zvols, the destination device	link
#      is destroyed and recreated, which means the zvol cannot be accessed
#      during	the receive operation.
#
#      When a	snapshot replication package stream that is generated by using
#      the "zfs send -R" command is received,	any snapshots that do not
#      exist on the sending location are destroyed by	using the "zfs destroy
#      -d" command.
#
#      The name of the snapshot (and file system, if a full stream is
#      received) that	this subcommand	creates	depends	on the argument	type
#      and the -d or -e option.
#
#      If the	argument is a snapshot name, the specified snapshot is cre-
#      ated. If the argument is a file system	or volume name,	a snapshot
#      with the same name as the sent	snapshot is created within the speci-
#      fied filesystem or volume.  If	the -d or -e option is specified, the
#      snapshot name is determined by	appending the sent snapshot's name to
#      the specified filesystem.  If the -d option is	specified, all but the
#      pool name of the sent snapshot	path is	appended (for example, b/c@1
#      appended from sent snapshot a/b/c@1), and if the -e option is speci-
#      fied, only the	tail of	the sent snapshot path is appended (for	exam-
#      ple, c@1 appended from	sent snapshot a/b/c@1).	 In the	case of	-d,
#      any file systems needed to replicate the path of the sent snapshot
#      are created within the	specified file system.
#
#      -d	 Use the full sent snapshot path without the first element
#          (without pool name) to	determine the name of the new snapshot
#          as described in the paragraph above.
#
#      -e	 Use only the last element of the sent snapshot	path to	deter-
#          mine the name of the new snapshot as described	in the para-
#          graph above.
#
#      -u	 File system that is associated	with the received stream is
#          not mounted.
#
#      -v	 Print verbose information about the stream and	the time
#          required to perform the receive operation.
#
#      -n	 Do not	actually receive the stream. This can be useful	in
#          conjunction with the -v option	to verify the name the receive
#          operation would use.
#
#      -o origin=snapshot
#          Forces	the stream to be received as a clone of	the given
#          snapshot.  If the stream is a full send stream, this will
#          create	the filesystem described by the	stream as a clone of
#          the specified snapshot. Which snapshot	was specified will not
#          affect	the success or failure of the receive, as long as the
#          snapshot does exist.  If the stream is	an incremental send
#          stream, all the normal	verification will be performed.
#
#      -F	 Force a rollback of the file system to	the most recent	snap-
#          shot before performing	the receive operation. If receiving an
#          incremental replication stream	(for example, one generated by
#          "zfs send -R {-i | -I}"), destroy snapshots and file systems
#          that do not exist on the sending side.
#
#      -s	 If the	receive	is interrupted,	save the partially received
#          state,	rather than deleting it.  Interruption may be due to
#          premature termination of the stream (e.g. due to network
#          failure or failure of the remote system if the	stream is
#          being read over a network connection),	a checksum error in
#          the stream, termination of the	zfs receive process, or
#          unclean shutdown of the system.
#
#          The receive can be resumed with a stream generated by zfs
#          send -t token,	where the token	is the value of	the
#          receive_resume_token property of the filesystem or volume
#          which is received into.
#
#          To use	this flag, the storage pool must have the
#          extensible_dataset feature enabled.  See zpool-features(5)
#          for details on	ZFS feature flags.
#
#      zfs receive|recv -A filesystem|volume
#      Abort an interrupted zfs receive -s, deleting its saved partially
#      received state.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_allow():
#     """
#      zfs allow filesystem|volume
#
#      Displays permissions that have	been delegated on the specified
#      filesystem or volume. See the other forms of "zfs allow" for more
#      information.
#
#      zfs allow [-ldug] user|group[,user|group]...
#      perm|@setname[,perm|@setname]... filesystem|volume
#
#      zfs allow [-ld] -e|everyone perm|@setname[,perm|@setname]...
#      filesystem|volume
#
#      Delegates ZFS administration permission for the file systems to non-
#      privileged users.
#
#      [-ug] user|group[, user|group]...
#          Specifies to whom the permissions are delegated. Multiple
#          entities can be specified as a	comma-separated	list. If nei-
#          ther of the -ug options are specified,	then the argument is
#          interpreted preferentially as the keyword everyone, then as a
#          user name, and	lastly as a group name.	To specify a user or
#          group named "everyone", use the -u or -g options. To specify
#          a group with the same name as a user, use the -g option.
#
#      [-e|everyone]
#          Specifies that	the permissions	be delegated to	"everyone".
#
#      perm|@setname[,perm|@setname]...
#          The permissions to delegate. Multiple permissions may be
#          specified as a	comma-separated	list. Permission names are the
#          same as ZFS subcommand	and property names. See	the property
#          list below. Property set names, which begin with an at	sign
#          (@), may be specified.	See the	-s form	below for details.
#
#      [-ld] filesystem|volume
#          Specifies where the permissions are delegated.	If neither of
#          the -ld options are specified,	or both	are, then the permis-
#          sions are allowed for the file	system or volume, and all of
#          its descendents. If only the -l option	is used, then is
#          allowed "locally" only	for the	specified file system.	If
#          only the -d option is used, then is allowed only for the
#          descendent file systems.
#
#      Permissions are generally the ability to use a	ZFS subcommand or
#      change	a ZFS property.	The following permissions are available:
#
#          NAME	       TYPE	     NOTES
#          allow	       subcommand    Must also have the	permission
#                          that is being allowed
#          clone	       subcommand    Must also have the	'create'
#                          ability and 'mount' ability in
#                          the origin	file system
#          create	       subcommand    Must also have the	'mount'
#                          ability
#          destroy	       subcommand    Must also have the	'mount'
#                          ability
#          diff	       subcommand    Allows lookup of paths within a
#                          dataset given an object number,
#                          and the ability to	create snap-
#                          shots necessary to	'zfs diff'
#          hold	       subcommand    Allows adding a user hold to a
#                          snapshot
#          mount	       subcommand    Allows mount/umount of ZFS
#                          datasets
#          promote	       subcommand    Must also have the	'mount'	and
#                          'promote' ability in the origin
#                          file system
#          receive	       subcommand    Must also have the	'mount'	and
#                          'create' ability
#          release	       subcommand    Allows releasing a	user hold
#                          which might destroy the snapshot
#          rename	       subcommand    Must also have the	'mount'	and
#                          'create' ability in the new
#                          parent
#          rollback	       subcommand    Must also have the	'mount'
#                          ability
#          send	       subcommand
#          share	       subcommand    Allows sharing file systems over
#                          the NFS protocol
#          snapshot	       subcommand    Must also have the	'mount'
#                          ability
#          groupquota	       other	     Allows accessing any
#                          groupquota@... property
#          groupused	       other	     Allows reading any	groupused@...
#                          property
#          userprop	       other	     Allows changing any user property
#          userquota	       other	     Allows accessing any
#                          userquota@... property
#          userused	       other	     Allows reading any	userused@...
#                          property
#          aclinherit	       property
#          aclmode	       property
#          atime	       property
#          canmount	       property
#          casesensitivity   property
#          checksum	       property
#          compression       property
#          copies	       property
#          dedup	       property
#          devices	       property
#          exec	       property
#          filesystem_limit  property
#          logbias	       property
#          jailed	       property
#          mlslabel	       property
#          mountpoint	       property
#          nbmand	       property
#          normalization     property
#          primarycache      property
#          quota	       property
#          readonly	       property
#          recordsize	       property
#          refquota	       property
#          refreservation    property
#          reservation       property
#          secondarycache    property
#          setuid	       property
#          sharenfs	       property
#          sharesmb	       property
#          snapdir	       property
#          snapshot_limit    property
#          sync	       property
#          utf8only	       property
#          version	       property
#          volblocksize      property
#          volsize	       property
#          vscan	       property
#          xattr	       property
#
#      zfs allow -c perm|@setname[,perm|@setname]... filesystem|volume
#
#      Sets "create time" permissions. These permissions are granted
#      (locally) to the creator of any newly-created descendent file system.
#
#      zfs allow -s @setname perm|@setname[,perm|@setname]... filesystem|volume
#
#      Defines or adds permissions to	a permission set. The set can be used
#      by other "zfs allow" commands for the specified file system and its
#      descendents. Sets are evaluated dynamically, so changes to a set are
#      immediately reflected.	Permission sets	follow the same	naming
#      restrictions as ZFS file systems, but the name	must begin with	an "at
#      sign" (@), and	can be no more than 64 characters long.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_unallow():
#     """
#      zfs unallow [-rldug] user|group[,user|group]...
#      [perm|@setname[,perm|@setname]...] filesystem|volume
#
#      zfs unallow [-rld]	-e|everyone [perm|@setname[,perm|@setname]...]
#      filesystem|volume
#
#      zfs unallow [-r] -c [perm|@setname[,perm|@setname]...] filesystem|volume
#
#      Removes permissions that were granted with the	"zfs allow" command.
#      No permissions	are explicitly denied, so other	permissions granted
#      are still in effect. For example, if the permission is	granted	by an
#      ancestor. If no permissions are specified, then all permissions for
#      the specified user, group, or everyone	are removed. Specifying
#      everyone (or using the	-e option) only	removes	the permissions	that
#      were granted to everyone, not all permissions for every user and
#      group.	See the	"zfs allow" command for	a description of the -ldugec
#      options.
#
#      -r	 Recursively remove the	permissions from this file system and
#          all descendents.
#
#      zfs unallow [-r] -s @setname [perm|@setname[,perm|@setname]...]
#      filesystem|volume
#
#      Removes permissions from a permission set. If no permissions are
#      specified, then all permissions are removed, thus removing the	set
#      entirely.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_hold():
#     """
#      zfs hold [-r] tag snapshot...
#
#      Adds a	single reference, named	with the tag argument, to the speci-
#      fied snapshot or snapshots. Each snapshot has its own tag namespace,
#      and tags must be unique within	that space.
#
#      If a hold exists on a snapshot, attempts to destroy that snapshot by
#      using the "zfs	destroy" command returns EBUSY.
#
#      -r	 Specifies that	a hold with the	given tag is applied recur-
#          sively	to the snapshots of all	descendent file	systems.
#
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_holds():
#     """
#      zfs holds [-Hp] [-r|-d depth] filesystem|volume|snapshot...
#
#      Lists all existing user references for	the given dataset or datasets.
#
#      -H	 Used for scripting mode. Do not print headers and separate
#          fields	by a single tab	instead	of arbitrary white space.
#
#      -p	 Display numbers in parsable (exact) values.
#
#      -r	 Lists the holds that are set on the descendent	snapshots of
#          the named datasets or snapshots, in addition to listing the
#          holds on the named snapshots, if any.
#
#      -d depth
#          Recursively display any holds on the named snapshots, or
#          descendent snapshots of the named datasets or snapshots, lim-
#          iting the recursion to	depth.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_release():
#     """
#      zfs release [-r] tag snapshot...
#
#      Removes a single reference, named with	the tag	argument, from the
#      specified snapshot or snapshots. The tag must already exist for each
#      snapshot.
#
#      -r	 Recursively releases a	hold with the given tag	on the snap-
#          shots of all descendent file systems.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# def zfs_diff():
#     """
#      zfs diff [-FHt] snapshot [snapshot|filesystem]
#
#      Display the difference	between	a snapshot of a	given filesystem and
#      another snapshot of that filesystem from a later time or the current
#      contents of the filesystem.  The first	column is a character indicat-
#      ing the type of change, the other columns indicate pathname, new
#      pathname (in case of rename), change in link count, and optionally
#      file type and/or change time.
#
#      The types of change are:
#
#        -	     path was removed
#        +	     path was added
#        M	     path was modified
#        R	     path was renamed
#
#      -F	 Display an indication of the type of file, in a manner	simi-
#          lar to	the -F option of ls(1).
#
#            B	     block device
#            C	     character device
#            F	     regular file
#            /	     directory
#            @	     symbolic link
#            =	     socket
#            >	     door (not supported on FreeBSD)
#            |	     named pipe	(not supported on FreeBSD)
#            P	     event port	(not supported on FreeBSD)
#
#      -H	 Give more parsable tab-separated output, without header lines
#          and without arrows.
#
#      -t	 Display the path's inode change time as the first column of
#          output.
#     """
#     if x is None:
#         raise TypeError(" name cannot be of type 'None'")
#
#     call_args = []
#
#     if y:
#         call_args.append("-r")
#
#     command = _Command("rollback", call_args, targets=[])
#
#     try:
#         return command.run()
#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(f"Failed to \n{e.output}\n")
#
#
# """FreeBSD Only"""
#
# """
#      zfs jail jailid filesystem
#
#      Attaches the specified	filesystem to the jail identified by JID
#      jailid.  From now on this file	system tree can	be managed from	within
#      a jail	if the jailed property has been	set. To	use this functional-
#      ity, the jail needs the allow.mount and allow.mount.zfs parameters
#      set to	1 and the enforce_statfs parameter set to a value lower	than
#      2.
#
#      See jail(8) for more information on managing jails and	configuring
#      the parameters	above.
#
#      zfs unjail	jailid filesystem
#
#      Detaches the specified	filesystem from	the jail identified by JID
#      jailid.
# """
