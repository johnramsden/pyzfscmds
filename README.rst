pyzfsutils
==========

.. image:: https://travis-ci.com/johnramsden/pyzfsutils.svg?token=4X1vWwTyHTHCUwBTudyN&branch=release/v0.1.0
    :target: https://travis-ci.com/johnramsden/pyzfsutils

ZFS CLI Function Wrapper

Requirements
------------

``pyzfsutils`` requires python 3.6+, and ZFS.

Installing
----------

``pyzfsutils`` can be installed by cloning the repo, and running the ``setup.py`` script.

.. code:: shell

    $ git clone https://github.com/johnramsden/pyzfsutils
    $ cd pyzfsutils
    $ python setup.py install

Testing
-------

To test, run ``pytest`` on the ``tests`` directory.

The following settings should be set:

- ``--unsafe`` - If used, more dangerous commands such as destroy will be run, otherwise they will be skipped.
- ``--zpool="${TEST_POOL}"``
- ``--test-dataset="${PYTEST_DATASET}"``
- ``--root-dataset="${TEST_POOL}/${TEST_ROOT}"``
- ``--zpool-root-mountpoint="${ZPOOL_MOUNTPOINT}/root"``

To test coverage, run ``pytest`` with the ``pytest-cov`` plugin.
To test pep8, run ``pytest`` with the ``pytest-pep8`` plugin.

Testing all at once:

.. code:: shell

    $ pytest --pep8 --cov=pyzfsutils tests \
                            --unsafe \
                            --zpool="${TEST_POOL}" \
                            --test-dataset="${PYTEST_DATASET}" \
                            --root-dataset="${TEST_POOL}/ROOT/default" \
                            --zpool-root-mountpoint="${ZPOOL_MOUNTPOINT}/root"
