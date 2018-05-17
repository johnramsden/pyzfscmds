import os

import pytest

module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")

require_root_dataset = pytest.mark.require_root_dataset
require_zpool_root_mountpoint = pytest.mark.require_zpool_root_mountpoint

"""zfs agnostic tests"""

# def test_mount():
#     pyzfscmds.system.a
