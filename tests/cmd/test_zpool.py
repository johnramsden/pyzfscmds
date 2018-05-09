import pytest
import datetime

import pyzfsutils.cmd

import os

module_env = os.path.basename(__file__).upper().rsplit('.', 1)[0]
if module_env in os.environ:
    pytestmark = pytest.mark.skipif(
        "false" in os.environ[module_env],
        reason=f"Environment variable {module_env} specified test should be skipped.")

"""zfs commands tests"""

require_zpool = pytest.mark.require_zpool
require_test_dataset = pytest.mark.require_test_dataset


@pytest.mark.parametrize("prop", [
    ["bootfs", "zpool"],
    ["bootfs", ""],
    ["comment", "Testcomment"],
    ["comment", ""]
])
@require_zpool
def test_zpool_set_successful(zpool, prop):

    pyzfsutils.cmd.zpool_set(zpool, "=".join(prop))

    assert prop[1] in pyzfsutils.cmd.zpool_get(zpool,
                                               properties=[prop[0]])
