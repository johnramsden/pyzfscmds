pyzfsutils
======

.. image:: https://travis-ci.com/johnramsden/pyzfsutils.svg?token=4X1vWwTyHTHCUwBTudyN&branch=release/v0.1.0
    :target: https://travis-ci.com/johnramsden/pyzfsutils

ZFS CLI Function Wrapper

Requirements
------------

``pyzfsutils`` requires python 3.6+, and ZFS.

Installing
---------

``pyzfsutils`` can be installed by cloning the repo, and running the ``setup.py`` script.

.. code:: shell

    $ git clone https://github.com/johnramsden/pyzfsutils
    $ cd pyzfsutils
    $ python setup.py install

Testing
-------

To test using pytest, run it from the tests directory with a zfs dataset.

.. code:: shell

    $ pytest --root-dataset="zpool/ROOT/default"

To test coverage run pytest wuth the pytest-cov plugin.

.. code:: shell

    $ pytest --root-dataset="zpool/ROOT/default" --cov=pyzfsutils
