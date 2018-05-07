#!/bin/sh

# Defaults if none give on cli
TEST_POOL="${TEST_POOL:-zpool}"
TEST_DATASET="${TEST_DATASET:-${TEST_POOL}/ROOT/default}"
ZDISKS_SUBDIR="${ZDISKS_SUBDIR:-zfstests}}"
ZPOOL_MOUNTPOINT="${ZPOOL_MOUNTPOINT:-zpool}"

TEST_DISK="${PWD}/${ZDISKS_SUBDIR}/disk.img"
ZPOOL_ROOT_MOUNTPOINT="${ZPOOL_MOUNTPOINT}/root"

modprobe zfs || exit 1

mkdir -p ${ZDISKS_SUBDIR} || exit 1

truncate -s 2G "${TEST_DISK}" && zpool create "${TEST_POOL}" "${TEST_DISK}"
if [ $? -ne 0 ]; then
    echo "Failed to create test pool ""'""${TEST_POOL}""'"" with disk ""'""${TEST_DISK}"
    exit 1
fi

mkdir -p "${ZPOOL_ROOT_MOUNTPOINT}" && \
zfs create -p -o mountpoint="${ZPOOL_ROOT_MOUNTPOINT}" "${TEST_DATASET}"
if [ $? -ne 0 ]; then
    echo "Failed to create test dataset ""'""${TEST_DATASET}""'"
    exit 1
fi

# Allow user usage of zfs
chmod u+s "$(which zfs)" "$(which zpool)" "$(which mount)" || exit 1
