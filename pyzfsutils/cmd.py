"""ZFS library"""

import itertools
import subprocess


class ZFS:
    @staticmethod
    def argcheck_depth(call_args, depth):
        if depth is not None:
            if depth < 0:
                raise RuntimeError("Depth cannot be negative")
            call_args.extend(["-d", str(depth)])

    @staticmethod
    def argcheck_columns(call_args, columns):
        if columns:
            if "all" in columns:
                call_args.extend(["-o", "all"])
            else:
                call_args.extend(["-o", ",".join(columns)])

    @staticmethod
    def _prepare_properties(properties: list):
        if properties is not None:
            prop_list = [["-o", prop] for prop in properties]
            return list(itertools.chain.from_iterable(prop_list))
        return []

    @staticmethod
    def _run(command, arguments):

        zfs_call = ["zfs", command] + arguments

        try:
            output = subprocess.check_output(zfs_call,
                                             universal_newlines=True,
                                             stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise e

        return output

    """
    ZFS commands
    """

    @classmethod
    def create_dataset(cls, filesystem: str, create_parent: bool = False,
                       mounted: bool = True, properties: list = None):

        if filesystem is None:
            raise TypeError("Filesystem name cannot be of type 'None'")

        call_args = []

        if create_parent:
            call_args = ["-p"]

        if not mounted:
            call_args.append('-u')

        """
        Combine all arguments with properties
        """
        call_args.extend(cls._prepare_properties(properties))

        """
        Specify source snapshot and filesystem
        """
        call_args.append(filesystem)

        try:
            return cls._run("create", call_args)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create {filesystem}\n{e.output}")

    @classmethod
    def create_zvol(cls, filesystem: str, blocksize: int, blocksize_suffix: str = "G",
                    create_parent: bool = False, sparse: bool = True, properties: list = None):

        if filesystem is None:
            raise TypeError("Filesystem name cannot be of type 'None'")

        call_args = []

        if create_parent:
            call_args = ["-p"]

        if sparse:
            call_args.append('-s')

        # TODO: blocksize

        """
        Combine all arguments with properties
        """
        call_args.extend(cls._prepare_properties(properties))

        """
        Specify source snapshot and filesystem
        """
        call_args.append(filesystem)

        try:
            return cls._run("create", call_args)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create {filesystem}\n{e.output}")

    @classmethod
    def clone(cls, snapname: str, filesystem: str, properties: list = None, create_parent=False):

        if snapname is None:
            raise TypeError("Snapshot name cannot be of type 'None'")

        call_args = []

        if create_parent:
            call_args = ["-p"]

        """
        Combine all arguments with properties
        """
        call_args.extend(cls._prepare_properties(properties))

        """
        Specify source snapshot and filesystem
        """
        call_args.extend([snapname, filesystem])

        try:
            return cls._run("clone", call_args)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone {filesystem}\n{e.output}")

    @classmethod
    def get(cls, target: str, recursive=False, depth: int = None, scripting=True,
            parsable=False, columns: list = None, zfs_types: list = None,
            source: list = None, properties: list = None):
        """
        zfs get [-r|-d depth] [-Hp] [-o all | field[,field]...]
         [-t type[, type]...] [-s source[,source]...] all |
         property[,property]...	filesystem|volume|snapshot...
        """

        call_args = []

        if recursive:
            call_args.append("-r")

        cls.argcheck_depth(call_args, depth)

        if scripting:
            call_args.append("-H")

        if parsable:
            call_args.append("-p")

        cls.argcheck_columns(call_args, columns)

        if zfs_types:
            call_args.extend(["-t", ",".join(zfs_types)])

        if source:
            call_args.extend(["-s", ",".join(source)])

        if properties is None:
            call_args.append("all")
        elif properties:
            if "all" in properties:
                if len(properties) < 2:
                    call_args.append("all")
                else:
                    raise RuntimeError(f"Cannot use 'all' with other properties")
            else:
                call_args.extend([",".join(properties)])
        else:
            raise RuntimeError(f"Cannot request no property type")

        call_args.append(target)

        try:
            return cls._run("get", call_args)
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Failed to get zfs properties of {target}")

    @classmethod
    def snapshot(cls, filesystem: str, snapname: str, recursive=False, properties=None):

        if snapname is None:
            raise TypeError("Snapshot name cannot be of type 'None'")

        call_args = []

        if recursive:
            call_args = ["-r"]

        """
        Combine all arguments with properties
        """
        call_args.extend(cls._prepare_properties(properties))

        """
        Specify source filesystem and  snapshot name
        """
        call_args.append(f"{filesystem}@{snapname}")

        try:
            cls._run("snapshot", call_args)
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Failed to snapshot {filesystem}")

    @classmethod
    def list(cls, target: str, recursive=False, depth: int = None, scripting=True,
             parsable=False, columns: list = None, zfs_types: list = None,
             sort_properties_ascending: list = None, sort_properties_descending: list = None):
        """
        zfs list [-r|-d depth] [-Hp] [-o property[,property]...]
            [-t type[,type]...] [-s property]... [-S property]...
            filesystem|volume|snapshot
        """

        call_args = []

        if recursive:
            call_args.append("-r")

        cls.argcheck_depth(call_args, depth)

        if scripting:
            call_args.append("-H")

        if parsable:
            call_args.append("-p")

        cls.argcheck_columns(call_args, columns)

        if zfs_types:
            call_args.extend(["-t", ",".join(zfs_types)])

        if sort_properties_ascending is not None:
            call_args.extend(
                [p for prop in sort_properties_ascending for p in ("-s", prop)])

        if sort_properties_descending is not None:
            call_args.extend(
                [p for prop in sort_properties_descending for p in ("-S", prop)])

        call_args.append(target)

        try:
            return cls._run("list", call_args)
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Failed to get zfs list of {target}")


class ZPOOL:
    """
    ZPOOL commands
    """
    @staticmethod
    def argcheck_depth(call_args, depth):
        if depth is not None:
            if depth < 0:
                raise RuntimeError("Depth cannot be negative")
            call_args.extend(["-d", str(depth)])

    @staticmethod
    def argcheck_columns(call_args, columns):
        if columns:
            if "all" in columns:
                call_args.extend(["-o", "all"])
            else:
                call_args.extend(["-o", ",".join(columns)])

    @staticmethod
    def _run(command, arguments):

        zfs_call = ["zpool", command] + arguments

        try:
            output = subprocess.check_output(zfs_call,
                                             universal_newlines=True,
                                             stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise e

        return output
