"""ZFS library"""

import itertools
import subprocess

"""
ZFS commands
"""


class _Command:

    def __init__(self, sub_command: str, options: list = None,
                 properties: list = None, targets: list = None, main_command: str = "zfs"):
        self.main_command = main_command
        self.sub_command = sub_command
        self.targets = targets

        self.call_args = [o for o in options] if options is not None else []

        if properties:
            self.properties = self._prepare_properties(properties)

    @staticmethod
    def _prepare_properties(properties: list):
        if properties is not None:
            prop_list = [["-o", prop] for prop in properties]
            return list(itertools.chain.from_iterable(prop_list))
        return []

    def argcheck_depth(self, depth):
        if depth is not None:
            if depth < 0:
                raise RuntimeError("Depth cannot be negative")
            self.call_args.extend(["-d", str(depth)])

    def argcheck_columns(self, columns):
        if columns:
            if "all" in columns:
                self.call_args.extend(["-o", "all"])
            else:
                self.call_args.extend(["-o", ",".join(columns)])

    def run(self):

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


def zfs_create_dataset(filesystem: str, create_parent: bool = False,
                       mounted: bool = True, properties: list = None):
    """
     zfs create	[-pu] [-o property=value]... filesystem
    """
    if filesystem is None:
        raise TypeError("Filesystem name cannot be of type 'None'")

    call_args = []

    if create_parent:
        call_args.append('-p')

    if not mounted:
        call_args.append('-u')

    create = _Command("create", call_args, properties=properties, targets=[filesystem])

    try:
        return create.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create {filesystem}\n{e.output}\n")


def zfs_create_zvol(filesystem: str, blocksize: int, blocksize_suffix: str = "G",
                    create_parent: bool = False, sparse: bool = True, properties: list = None):
    """
     zfs create	[-ps] [-b blocksize] [-o property=value]... -V size volume
    """
    if filesystem is None:
        raise TypeError("Filesystem name cannot be of type 'None'")

    call_args = []

    if create_parent:
        call_args = ["-p"]

    if sparse:
        call_args.append('-s')

    call_args.extend(['-b', f"{str(blocksize)}{blocksize_suffix}"])

    command = _Command("create", call_args, properties=properties, targets=[filesystem])

    try:
        return command.run()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create {filesystem}\n{e.output}\n")


def zfs_clone(snapname: str, filesystem: str, properties: list = None, create_parent=False):
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


def zfs_snapshot(filesystem: str, snapname: str, recursive=False, properties=None):
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


def zfs_get(target: str, recursive=False, depth: int = None, scripting=True,
            parsable=False, columns: list = None, zfs_types: list = None,
            source: list = None, properties: list = None):
    """
     zfs get [-r|-d depth] [-Hp] [-o all | field[,field]...] [-t
     type[,type]...] [-s source[,source]...] all | property[,property]...
     filesystem|volume|snapshot...

     Displays properties for the given datasets. If	no datasets are	speci-
     fied, then the	command	displays properties for	all datasets on	the
     system. For each property, the	following columns are displayed:

           name	 Dataset name
           property	 Property name
           value	 Property value
           source	 Property source. Can either be	local, default,	tempo-
             rary, inherited, received, or none (-).

     All columns except the	RECEIVED column	are displayed by default. The
     columns to display can	be specified by	using the -o option. This com-
     mand takes a comma-separated list of properties as described in the
     "Native Properties" and "User Properties" sections.

     The special value all can be used to display all properties that
     apply to the given dataset's type (filesystem,	volume,	snapshot, or
     bookmark).

     -r	 Recursively display properties	for any	children.

     -d depth
         Recursively display any children of the dataset, limiting the
         recursion to depth.  A	depth of 1 will	display	only the
         dataset and its direct	children.

     -H	 Display output	in a form more easily parsed by	scripts. Any
         headers are omitted, and fields are explicitly	separated by a
         single	tab instead of an arbitrary amount of space.

     -p	 Display numbers in parsable (exact) values.

     -o all	| field[,field]...
         A comma-separated list	of columns to display. Supported val-
         ues are name,property,value,received,source.  Default values
         are name,property,value,source.  The keyword all specifies
         all columns.

     -t type[,type]...
         A comma-separated list	of types to display, where type	is one
         of filesystem,	snapshot, volume, or all.  For example,	speci-
         fying -t snapshot displays only snapshots.

     -s source[,source]...
         A comma-separated list	of sources to display. Those proper-
         ties coming from a source other than those in this list are
         ignored. Each source must be one of the following:
         local,default,inherited,temporary,received,none.  The default
         value is all sources.
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


def zfs_list(target: str, recursive=False, depth: int = None, scripting=True,
             parsable=False, columns: list = None, zfs_types: list = None,
             sort_properties_ascending: list = None, sort_properties_descending: list = None):
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


# TODO: Remaining commands


def zfs_destroy():
    """
    zfs destroy [-fnpRrv] filesystem|volume

    Destroys the given dataset. By	default, the command unshares any file
    systems that are currently shared, unmounts any file systems that are
    currently mounted, and	refuses	to destroy a dataset that has active
    dependents (children or clones).

    -r	 Recursively destroy all children.

    -R	 Recursively destroy all dependents, including cloned file
         systems outside the target hierarchy.

    -f	 Force an unmount of any file systems using the	"zfs unmount
         -f" command. This option has no effect	on non-file systems or
         unmounted file	systems.

    -n	 Do a dry-run ("No-op")	deletion. No data will be deleted.
         This is useful	in conjunction with the	-v or -p flags to
         determine what	data would be deleted.

    -p	 Print machine-parsable	verbose	information about the deleted
         data.

    -v	 Print verbose information about the deleted data.

    Extreme care should be	taken when applying either the -r or the -R
    options, as they can destroy large portions of	a pool and cause unex-
    pected	behavior for mounted file systems in use.
    """
    pass


def zfs_destroy_snapshot():
    """
     zfs destroy [-dnpRrv] snapshot[%snapname][,...]

     The given snapshots are destroyed immediately if and only if the "zfs
     destroy" command without the -d option	would have destroyed it. Such
     immediate destruction would occur, for	example, if the	snapshot had
     no clones and the user-initiated reference count were zero.

     If a snapshot does not	qualify	for immediate destruction, it is
     marked	for deferred deletion. In this state, it exists	as a usable,
     visible snapshot until	both of	the preconditions listed above are
     met, at which point it	is destroyed.

     An inclusive range of snapshots may be	specified by separating	the
     first and last	snapshots with a percent sign (%).  The	first and/or
     last snapshots	may be left blank, in which case the filesystem's old-
     est or	newest snapshot	will be	implied.

     Multiple snapshots (or	ranges of snapshots) of	the same filesystem or
     volume	may be specified in a comma-separated list of snapshots.  Only
     the snapshot's	short name (the	part after the @) should be specified
     when using a range or comma-separated list to identify	multiple snap-
     shots.

     -r	 Destroy (or mark for deferred deletion) all snapshots with
         this name in descendent file systems.

     -R	 Recursively destroy all clones	of these snapshots, including
         the clones, snapshots,	and children.  If this flag is speci-
         fied, the -d flag will	have no	effect.

     -n	 Do a dry-run ("No-op")	deletion. No data will be deleted.
         This is useful	in conjunction with the	-v or -p flags to
         determine what	data would be deleted.

     -p	 Print machine-parsable	verbose	information about the deleted
         data.

     -v	 Print verbose information about the deleted data.

     -d	 Defer snapshot	deletion.

     Extreme care should be	taken when applying either the -r or the -R
     options, as they can destroy large portions of	a pool and cause unex-
     pected	behavior for mounted file systems in use.
    """
    pass


def zfs_destroy_bookmark():
    """
     zfs destroy filesystem|volume#bookmark

     The given bookmark is destroyed.
    """
    pass


def zfs_rollback():
    """
     zfs rollback [-rRf] snapshot

     Roll back the given dataset to	a previous snapshot. When a dataset is
     rolled	back, all data that has	changed	since the snapshot is dis-
     carded, and the dataset reverts to the	state at the time of the snap-
     shot. By default, the command refuses to roll back to a snapshot
     other than the	most recent one. In order to do	so, all	intermediate
     snapshots and bookmarks must be destroyed by specifying the -r
     option.

     The -rR options do not	recursively destroy the	child snapshots	of a
     recursive snapshot.  Only direct snapshots of the specified filesys-
     tem are destroyed by either of	these options.	To completely roll
     back a	recursive snapshot, you	must rollback the individual child
     snapshots.

     -r	 Destroy any snapshots and bookmarks more recent than the one
         specified.

     -R	 Destroy any more recent snapshots and bookmarks, as well as
         any clones of those snapshots.

     -f	 Used with the -R option to force an unmount of	any clone file
         systems that are to be	destroyed.
    """
    pass


def zfs_promote():
    """
     zfs promote clone-filesystem

     Promotes a clone file system to no longer be dependent	on its "ori-
     gin" snapshot.	This makes it possible to destroy the file system that
     the clone was created from. The clone parent-child dependency rela-
     tionship is reversed, so that the origin file system becomes a	clone
     of the	specified file system.

     The snapshot that was cloned, and any snapshots previous to this
     snapshot, are now owned by the	promoted clone.	The space they use
     moves from the	origin file system to the promoted clone, so enough
     space must be available to accommodate	these snapshots. No new	space
     is consumed by	this operation,	but the	space accounting is adjusted.
     The promoted clone must not have any conflicting snapshot names of
     its own. The rename subcommand	can be used to rename any conflicting
     snapshots.

    """
    pass


def zfs_rename():
    """
     zfs rename	[-f] filesystem|volume|snapshot	filesystem|volume|snapshot

     zfs rename	[-f] -p	filesystem|volume filesystem|volume

     zfs rename	-u [-p]	filesystem filesystem

     Renames the given dataset. The	new target can be located anywhere in
     the ZFS hierarchy, with the exception of snapshots. Snapshots can
     only be renamed within	the parent file	system or volume. When renam-
     ing a snapshot, the parent file system	of the snapshot	does not need
     to be specified as part of the	second argument. Renamed file systems
     can inherit new mount points, in which	case they are unmounted	and
     remounted at the new mount point.

     -p	 Creates all the nonexistent parent datasets. Datasets created
         in this manner	are automatically mounted according to the
         mountpoint property inherited from their parent.

     -u	 Do not	remount	file systems during rename. If a file system's
         mountpoint property is	set to legacy or none, file system is
         not unmounted even if this option is not given.

     -f	 Force unmount any filesystems that need to be unmounted in
         the process.  This flag has no	effect if used together	with
         the -u	flag.

             zfs rename	-r snapshot snapshot

     Recursively rename the	snapshots of all descendent datasets. Snap-
     shots are the only dataset that can be	renamed	recursively.
    """
    pass


def zfs_set():
    """
     zfs set property=value [property=value]...	filesystem|volume|snapshot

     Sets the property or list of properties to the	given value(s) for
     each dataset.	Only some properties can be edited. See	the "Proper-
     ties" section for more	information on what properties can be set and
     acceptable values. Numeric values can be specified as exact values,
     or in a human-readable	form with a suffix of B, K, M, G, T, P,	E, Z
     (for bytes, kilobytes,	megabytes, gigabytes, terabytes, petabytes,
     exabytes, or zettabytes, respectively). User properties can be	set on
     snapshots. For	more information, see the "User	Properties" section.
    """
    pass


def zfs_inherit():
    """
     zfs inherit [-rS] property	filesystem|volume|snapshot...

     Clears	the specified property,	causing	it to be inherited from	an
     ancestor, restored to default if no ancestor has the property set, or
     with the -S option reverted to	the received value if one exists.  See
     the "Properties" section for a	listing	of default values, and details
     on which properties can be inherited.

     -r	 Recursively inherit the given property	for all	children.

     -S	 Revert	the property to	the received value if one exists; oth-
         erwise	operate	as if the -S option was	not specified.
    """
    pass


def zfs_upgrade():
    """
     zfs upgrade [-v]

     Displays a list of file systems that are not the most recent version.

     -v	 Displays ZFS filesystem versions supported by the current
         software. The current ZFS filesystem version and all previous
         supported versions are	displayed, along with an explanation
         of the	features provided with each version.

     zfs upgrade [-r] [-V version] -a |	filesystem

     Upgrades file systems to a new	on-disk	version. Once this is done,
     the file systems will no longer be accessible on systems running
     older versions	of the software.  "zfs send" streams generated from
     new snapshots of these	file systems cannot be accessed	on systems
     running older versions	of the software.

     In general, the file system version is	independent of the pool	ver-
     sion. See zpool(8) for	information on the zpool upgrade command.

     In some cases,	the file system	version	and the	pool version are
     interrelated and the pool version must	be upgraded before the file
     system	version	can be upgraded.

     -r	 Upgrade the specified file system and all descendent file
         systems.

     -V version
         Upgrade to the	specified version.  If the -V flag is not
         specified, this command upgrades to the most recent version.
         This option can only be used to increase the version number,
         and only up to	the most recent	version	supported by this
         software.

     -a	 Upgrade all file systems on all imported pools.

     filesystem
         Upgrade the specified file system.
    """
    pass


def zfs_userspace():
    """
     zfs userspace [-Hinp] [-o field[,field]...] [-s field]... [-S field]...
     [-t type[,type]...] filesystem|snapshot

     Displays space	consumed by, and quotas	on, each user in the specified
     filesystem or snapshot. This corresponds to the userused@user and
     userquota@user	properties.

     -n	 Print numeric ID instead of user/group	name.

     -H	 Do not	print headers, use tab-delimited output.

     -p	 Use exact (parsable) numeric output.

     -o field[,field]...
         Display only the specified fields from	the following set:
         type,name,used,quota.	The default is to display all fields.

     -s field
         Sort output by	this field. The	-s and -S flags	may be speci-
         fied multiple times to	sort first by one field, then by
         another. The default is -s type -s name.

     -S field
         Sort by this field in reverse order. See -s.

     -t type[,type]...
         Print only the	specified types	from the following set:
         all,posixuser,smbuser,posixgroup,smbgroup.

         The default is	-t posixuser,smbuser.

         The default can be changed to include group types.

     -i	 Translate SID to POSIX	ID. This flag currently	has no effect
         on FreeBSD.
    """
    pass


def zfs_groupspace():
    """
     zfs groupspace [-Hinp] [-o	field[,field]...] [-s field]...	[-S field]...
     [-t type[,type]...] filesystem|snapshot

     Displays space	consumed by, and quotas	on, each group in the speci-
     fied filesystem or snapshot. This subcommand is identical to "zfs
     userspace", except that the default types to display are -t
     posixgroup,smbgroup.
    """
    pass


def zfs_mount():
    """
     zfs mount

     Displays all ZFS file systems currently mounted.

     -f

     zfs mount [-vO] [-o property[,property]...] -a | filesystem

     Mounts	ZFS file systems.

     -v	 Report	mount progress.

     -O	 Perform an overlay mount. Overlay mounts are not supported on
         FreeBSD.

     -o property[,property]...
         An optional, comma-separated list of mount options to use
         temporarily for the duration of the mount. See	the "Temporary
         Mount Point Properties" section for details.

     -a	 Mount all available ZFS file systems.	This command may be
         executed on FreeBSD system startup by /etc/rc.d/zfs.  For
         more information, see variable	zfs_enable in rc.conf(5).

     filesystem
         Mount the specified filesystem.
    """
    pass


def zfs_unmount():
    """
     zfs unmount|umount	[-f] -a	| filesystem|mountpoint

     Unmounts currently mounted ZFS	file systems.

     -f	 Forcefully unmount the	file system, even if it	is currently
         in use.

     -a	 Unmount all available ZFS file	systems.

     filesystem | mountpoint
         Unmount the specified filesystem. The command can also	be
         given a path to a ZFS file system mount point on the system.
    """
    pass


def zfs_share():
    """
     zfs share -a | filesystem

     Shares	ZFS file systems that have the sharenfs	property set.

     -a	 Share all ZFS file systems that have the sharenfs property
         set.  This command may	be executed on FreeBSD system startup
         by /etc/rc.d/zfs.  For	more information, see variable
         zfs_enable in rc.conf(5).

     filesystem
         Share the specified filesystem	according to the sharenfs
         property. File	systems	are shared when	the sharenfs property
         is set.
    """
    pass


def zfs_unshare():
    """
   zfs unshare -a | filesystem|mountpoint

     Unshares ZFS file systems that	have the sharenfs property set.

     -a	 Unshares ZFS file systems that	have the sharenfs property
         set.  This command may	be executed on FreeBSD system shutdown
         by /etc/rc.d/zfs.  For	more information, see variable
         zfs_enable in rc.conf(5).

     filesystem | mountpoint
         Unshare the specified filesystem. The command can also	be
         given a path to a ZFS file system shared on the system.
    """
    pass


def zfs_bookmark():
    """
     zfs bookmark snapshot bookmark

     Creates a bookmark of the given snapshot.  Bookmarks mark the point
     in time when the snapshot was created,	and can	be used	as the incre-
     mental	source for a "zfs send"	command.

     This feature must be enabled to be used.  See zpool-features(7) for
     details on ZFS	feature	flags and the bookmark feature.
    """
    pass


def zfs_send():
    """
     zfs send [-DnPpRveL] [-i snapshot | -I snapshot] snapshot

     Creates a stream representation of the	last snapshot argument (not
     part of -i or -I) which is written to standard	output.	The output can
     be redirected to a file or to a different system (for example,	using
     ssh(1)).  By default, a full stream is	generated.

     -i snapshot
         Generate an incremental stream	from the first snapshot	(the
         incremental source) to	the second snapshot (the incremental
         target).  The incremental source can be specified as the last
         component of the snapshot name	(the @ character and
         following) and	it is assumed to be from the same file system
         as the	incremental target.

         If the	destination is a clone,	the source may be the origin
         snapshot, which must be fully specified (for example,
         pool/fs@origin, not just @origin).

     -I snapshot
         Generate a stream package that	sends all intermediary snap-
         shots from the	first snapshot to the second snapshot.	For
         example, -I @a	fs@d is	similar	to -i @a fs@b; -i @b fs@c; -i
         @c fs@d.  The incremental source may be specified as with the
         -i option.

     -R	 Generate a replication	stream package,	which will replicate
         the specified filesystem, and all descendent file systems, up
         to the	named snapshot.	When received, all properties, snap-
         shots,	descendent file	systems, and clones are	preserved.

         If the	-i or -I flags are used	in conjunction with the	-R
         flag, an incremental replication stream is generated. The
         current values	of properties, and current snapshot and	file
         system	names are set when the stream is received. If the -F
         flag is specified when	this stream is received, snapshots and
         file systems that do not exist	on the sending side are
         destroyed.

     -D	 Generate a deduplicated stream. Blocks	which would have been
         sent multiple times in	the send stream	will only be sent
         once.	The receiving system must also support this feature to
         receive a deduplicated	stream.	 This flag can be used regard-
         less of the dataset's dedup property, but performance will be
         much better if	the filesystem uses a dedup-capable checksum
         (eg.  sha256).

     -L	 Generate a stream which may contain blocks larger than	128KB.
         This flag has no effect if the	large_blocks pool feature is
         disabled, or if the recordsize	property of this filesystem
         has never been	set above 128KB.  The receiving	system must
         have the large_blocks pool feature enabled as well.  See
         zpool-features(7) for details on ZFS feature flags and	the
         large_blocks feature.

     -e	 Generate a more compact stream	by using WRITE_EMBEDDED
         records for blocks which are stored more compactly on disk by
         the embedded_data pool	feature.  This flag has	no effect if
         the embedded_data feature is disabled.	 The receiving system
         must have the embedded_data feature enabled.  If the
         lz4_compress feature is active	on the sending system, then
         the receiving system must have	that feature enabled as	well.
         See zpool-features(7) for details on ZFS feature flags	and
         the embedded_data feature.

     -p	 Include the dataset's properties in the stream. This flag is
         implicit when -R is specified.	The receiving system must also
         support this feature.

     -n	 Do a dry-run ("No-op")	send.  Do not generate any actual send
         data.	This is	useful in conjunction with the -v or -P	flags
         to determine what data	will be	sent.  In this case, the ver-
         bose output will be written to	standard output	(contrast with
         a non-dry-run,	where the stream is written to standard	output
         and the verbose output	goes to	standard error).

     -P	 Print machine-parsable	verbose	information about the stream
         package generated.

     -v	 Print verbose information about the stream package generated.
         This information includes a per-second	report of how much
         data has been sent.

     The format of the stream is committed.	You will be able to receive
     your streams on future	versions of ZFS.

     zfs send [-eL] [-i	snapshot|bookmark] filesystem|volume|snapshot

     Generate a send stream, which may be of a filesystem, and may be
     incremental from a bookmark.  If the destination is a filesystem or
     volume, the pool must be read-only, or	the filesystem must not	be
     mounted.  When	the stream generated from a filesystem or volume is
     received, the default snapshot	name will be (--head--).

     -i snapshot|bookmark
         Generate an incremental send stream.  The incremental source
         must be an earlier snapshot in	the destination's history.  It
         will commonly be an earlier snapshot in the destination's
         filesystem, in	which case it can be specified as the last
         component of the name (the # or @ character and following).

         If the	incremental target is a	clone, the incremental source
         can be	the origin snapshot, or	an earlier snapshot in the
         origin's filesystem, or the origin's origin, etc.

     -L	 Generate a stream which may contain blocks larger than	128KB.
         This flag has no effect if the	large_blocks pool feature is
         disabled, or if the recordsize	property of this filesystem
         has never been	set above 128KB.  The receiving	system must
         have the large_blocks pool feature enabled as well.  See
         zpool-features(7) for details on ZFS feature flags and	the
         large_blocks feature.

     -e	 Generate a more compact stream	by using WRITE_EMBEDDED
         records for blocks which are stored more compactly on disk by
         the embedded_data pool	feature.  This flag has	no effect if
         the embedded_data feature is disabled.	 The receiving system
         must have the embedded_data feature enabled.  If the
         lz4_compress feature is active	on the sending system, then
         the receiving system must have	that feature enabled as	well.
         See zpool-features(7) for details on ZFS feature flags	and
         the embedded_data feature.

     zfs send [-Penv] -t receive_resume_token
     Creates a send	stream which resumes an	interrupted receive.  The
     receive_resume_token is the value of this property on the filesystem
     or volume that	was being received into.  See the documentation	for
     zfs receive -s	for more details.
    """
    pass


def zfs_receive():
    """
     zfs receive|recv [-vnsFu] [-o origin=snapshot] filesystem|volume|snapshot

     zfs receive|recv [-vnsFu] [-d | -e] [-o origin=snapshot] filesystem

     Creates a snapshot whose contents are as specified in the stream pro-
     vided on standard input. If a full stream is received,	then a new
     file system is	created	as well. Streams are created using the "zfs
     send" subcommand, which by default creates a full stream.  "zfs recv"
     can be	used as	an alias for "zfs receive".

     If an incremental stream is received, then the	destination file sys-
     tem must already exist, and its most recent snapshot must match the
     incremental stream's source. For zvols, the destination device	link
     is destroyed and recreated, which means the zvol cannot be accessed
     during	the receive operation.

     When a	snapshot replication package stream that is generated by using
     the "zfs send -R" command is received,	any snapshots that do not
     exist on the sending location are destroyed by	using the "zfs destroy
     -d" command.

     The name of the snapshot (and file system, if a full stream is
     received) that	this subcommand	creates	depends	on the argument	type
     and the -d or -e option.

     If the	argument is a snapshot name, the specified snapshot is cre-
     ated. If the argument is a file system	or volume name,	a snapshot
     with the same name as the sent	snapshot is created within the speci-
     fied filesystem or volume.  If	the -d or -e option is specified, the
     snapshot name is determined by	appending the sent snapshot's name to
     the specified filesystem.  If the -d option is	specified, all but the
     pool name of the sent snapshot	path is	appended (for example, b/c@1
     appended from sent snapshot a/b/c@1), and if the -e option is speci-
     fied, only the	tail of	the sent snapshot path is appended (for	exam-
     ple, c@1 appended from	sent snapshot a/b/c@1).	 In the	case of	-d,
     any file systems needed to replicate the path of the sent snapshot
     are created within the	specified file system.

     -d	 Use the full sent snapshot path without the first element
         (without pool name) to	determine the name of the new snapshot
         as described in the paragraph above.

     -e	 Use only the last element of the sent snapshot	path to	deter-
         mine the name of the new snapshot as described	in the para-
         graph above.

     -u	 File system that is associated	with the received stream is
         not mounted.

     -v	 Print verbose information about the stream and	the time
         required to perform the receive operation.

     -n	 Do not	actually receive the stream. This can be useful	in
         conjunction with the -v option	to verify the name the receive
         operation would use.

     -o origin=snapshot
         Forces	the stream to be received as a clone of	the given
         snapshot.  If the stream is a full send stream, this will
         create	the filesystem described by the	stream as a clone of
         the specified snapshot. Which snapshot	was specified will not
         affect	the success or failure of the receive, as long as the
         snapshot does exist.  If the stream is	an incremental send
         stream, all the normal	verification will be performed.

     -F	 Force a rollback of the file system to	the most recent	snap-
         shot before performing	the receive operation. If receiving an
         incremental replication stream	(for example, one generated by
         "zfs send -R {-i | -I}"), destroy snapshots and file systems
         that do not exist on the sending side.

     -s	 If the	receive	is interrupted,	save the partially received
         state,	rather than deleting it.  Interruption may be due to
         premature termination of the stream (e.g. due to network
         failure or failure of the remote system if the	stream is
         being read over a network connection),	a checksum error in
         the stream, termination of the	zfs receive process, or
         unclean shutdown of the system.

         The receive can be resumed with a stream generated by zfs
         send -t token,	where the token	is the value of	the
         receive_resume_token property of the filesystem or volume
         which is received into.

         To use	this flag, the storage pool must have the
         extensible_dataset feature enabled.  See zpool-features(5)
         for details on	ZFS feature flags.

     zfs receive|recv -A filesystem|volume
     Abort an interrupted zfs receive -s, deleting its saved partially
     received state.
    """
    pass


def zfs_allow():
    """
     zfs allow filesystem|volume

     Displays permissions that have	been delegated on the specified
     filesystem or volume. See the other forms of "zfs allow" for more
     information.

     zfs allow [-ldug] user|group[,user|group]...
     perm|@setname[,perm|@setname]... filesystem|volume

     zfs allow [-ld] -e|everyone perm|@setname[,perm|@setname]...
     filesystem|volume

     Delegates ZFS administration permission for the file systems to non-
     privileged users.

     [-ug] user|group[, user|group]...
         Specifies to whom the permissions are delegated. Multiple
         entities can be specified as a	comma-separated	list. If nei-
         ther of the -ug options are specified,	then the argument is
         interpreted preferentially as the keyword everyone, then as a
         user name, and	lastly as a group name.	To specify a user or
         group named "everyone", use the -u or -g options. To specify
         a group with the same name as a user, use the -g option.

     [-e|everyone]
         Specifies that	the permissions	be delegated to	"everyone".

     perm|@setname[,perm|@setname]...
         The permissions to delegate. Multiple permissions may be
         specified as a	comma-separated	list. Permission names are the
         same as ZFS subcommand	and property names. See	the property
         list below. Property set names, which begin with an at	sign
         (@), may be specified.	See the	-s form	below for details.

     [-ld] filesystem|volume
         Specifies where the permissions are delegated.	If neither of
         the -ld options are specified,	or both	are, then the permis-
         sions are allowed for the file	system or volume, and all of
         its descendents. If only the -l option	is used, then is
         allowed "locally" only	for the	specified file system.	If
         only the -d option is used, then is allowed only for the
         descendent file systems.

     Permissions are generally the ability to use a	ZFS subcommand or
     change	a ZFS property.	The following permissions are available:

         NAME	       TYPE	     NOTES
         allow	       subcommand    Must also have the	permission
                         that is being allowed
         clone	       subcommand    Must also have the	'create'
                         ability and 'mount' ability in
                         the origin	file system
         create	       subcommand    Must also have the	'mount'
                         ability
         destroy	       subcommand    Must also have the	'mount'
                         ability
         diff	       subcommand    Allows lookup of paths within a
                         dataset given an object number,
                         and the ability to	create snap-
                         shots necessary to	'zfs diff'
         hold	       subcommand    Allows adding a user hold to a
                         snapshot
         mount	       subcommand    Allows mount/umount of ZFS
                         datasets
         promote	       subcommand    Must also have the	'mount'	and
                         'promote' ability in the origin
                         file system
         receive	       subcommand    Must also have the	'mount'	and
                         'create' ability
         release	       subcommand    Allows releasing a	user hold
                         which might destroy the snapshot
         rename	       subcommand    Must also have the	'mount'	and
                         'create' ability in the new
                         parent
         rollback	       subcommand    Must also have the	'mount'
                         ability
         send	       subcommand
         share	       subcommand    Allows sharing file systems over
                         the NFS protocol
         snapshot	       subcommand    Must also have the	'mount'
                         ability
         groupquota	       other	     Allows accessing any
                         groupquota@... property
         groupused	       other	     Allows reading any	groupused@...
                         property
         userprop	       other	     Allows changing any user property
         userquota	       other	     Allows accessing any
                         userquota@... property
         userused	       other	     Allows reading any	userused@...
                         property
         aclinherit	       property
         aclmode	       property
         atime	       property
         canmount	       property
         casesensitivity   property
         checksum	       property
         compression       property
         copies	       property
         dedup	       property
         devices	       property
         exec	       property
         filesystem_limit  property
         logbias	       property
         jailed	       property
         mlslabel	       property
         mountpoint	       property
         nbmand	       property
         normalization     property
         primarycache      property
         quota	       property
         readonly	       property
         recordsize	       property
         refquota	       property
         refreservation    property
         reservation       property
         secondarycache    property
         setuid	       property
         sharenfs	       property
         sharesmb	       property
         snapdir	       property
         snapshot_limit    property
         sync	       property
         utf8only	       property
         version	       property
         volblocksize      property
         volsize	       property
         vscan	       property
         xattr	       property

     zfs allow -c perm|@setname[,perm|@setname]... filesystem|volume

     Sets "create time" permissions. These permissions are granted
     (locally) to the creator of any newly-created descendent file system.

     zfs allow -s @setname perm|@setname[,perm|@setname]... filesystem|volume

     Defines or adds permissions to	a permission set. The set can be used
     by other "zfs allow" commands for the specified file system and its
     descendents. Sets are evaluated dynamically, so changes to a set are
     immediately reflected.	Permission sets	follow the same	naming
     restrictions as ZFS file systems, but the name	must begin with	an "at
     sign" (@), and	can be no more than 64 characters long.
    """
    pass


def zfs_unallow():
    """
     zfs unallow [-rldug] user|group[,user|group]...
     [perm|@setname[,perm|@setname]...] filesystem|volume

     zfs unallow [-rld]	-e|everyone [perm|@setname[,perm|@setname]...]
     filesystem|volume

     zfs unallow [-r] -c [perm|@setname[,perm|@setname]...] filesystem|volume

     Removes permissions that were granted with the	"zfs allow" command.
     No permissions	are explicitly denied, so other	permissions granted
     are still in effect. For example, if the permission is	granted	by an
     ancestor. If no permissions are specified, then all permissions for
     the specified user, group, or everyone	are removed. Specifying
     everyone (or using the	-e option) only	removes	the permissions	that
     were granted to everyone, not all permissions for every user and
     group.	See the	"zfs allow" command for	a description of the -ldugec
     options.

     -r	 Recursively remove the	permissions from this file system and
         all descendents.

     zfs unallow [-r] -s @setname [perm|@setname[,perm|@setname]...]
     filesystem|volume

     Removes permissions from a permission set. If no permissions are
     specified, then all permissions are removed, thus removing the	set
     entirely.
    """
    pass


def zfs_hold():
    """
     zfs hold [-r] tag snapshot...

     Adds a	single reference, named	with the tag argument, to the speci-
     fied snapshot or snapshots. Each snapshot has its own tag namespace,
     and tags must be unique within	that space.

     If a hold exists on a snapshot, attempts to destroy that snapshot by
     using the "zfs	destroy" command returns EBUSY.

     -r	 Specifies that	a hold with the	given tag is applied recur-
         sively	to the snapshots of all	descendent file	systems.

    """
    pass


def zfs_holds():
    """
     zfs holds [-Hp] [-r|-d depth] filesystem|volume|snapshot...

     Lists all existing user references for	the given dataset or datasets.

     -H	 Used for scripting mode. Do not print headers and separate
         fields	by a single tab	instead	of arbitrary white space.

     -p	 Display numbers in parsable (exact) values.

     -r	 Lists the holds that are set on the descendent	snapshots of
         the named datasets or snapshots, in addition to listing the
         holds on the named snapshots, if any.

     -d depth
         Recursively display any holds on the named snapshots, or
         descendent snapshots of the named datasets or snapshots, lim-
         iting the recursion to	depth.
    """
    pass


def zfs_release():
    """
     zfs release [-r] tag snapshot...

     Removes a single reference, named with	the tag	argument, from the
     specified snapshot or snapshots. The tag must already exist for each
     snapshot.

     -r	 Recursively releases a	hold with the given tag	on the snap-
         shots of all descendent file systems.
    """
    pass


def zfs_diff():
    """
     zfs diff [-FHt] snapshot [snapshot|filesystem]

     Display the difference	between	a snapshot of a	given filesystem and
     another snapshot of that filesystem from a later time or the current
     contents of the filesystem.  The first	column is a character indicat-
     ing the type of change, the other columns indicate pathname, new
     pathname (in case of rename), change in link count, and optionally
     file type and/or change time.

     The types of change are:

       -	     path was removed
       +	     path was added
       M	     path was modified
       R	     path was renamed

     -F	 Display an indication of the type of file, in a manner	simi-
         lar to	the -F option of ls(1).

           B	     block device
           C	     character device
           F	     regular file
           /	     directory
           @	     symbolic link
           =	     socket
           >	     door (not supported on FreeBSD)
           |	     named pipe	(not supported on FreeBSD)
           P	     event port	(not supported on FreeBSD)

     -H	 Give more parsable tab-separated output, without header lines
         and without arrows.

     -t	 Display the path's inode change time as the first column of
         output.
    """
    pass


"""FreeBSD Only"""

"""
     zfs jail jailid filesystem

     Attaches the specified	filesystem to the jail identified by JID
     jailid.  From now on this file	system tree can	be managed from	within
     a jail	if the jailed property has been	set. To	use this functional-
     ity, the jail needs the allow.mount and allow.mount.zfs parameters
     set to	1 and the enforce_statfs parameter set to a value lower	than
     2.

     See jail(8) for more information on managing jails and	configuring
     the parameters	above.

     zfs unjail	jailid filesystem

     Detaches the specified	filesystem from	the jail identified by JID
     jailid.
"""
