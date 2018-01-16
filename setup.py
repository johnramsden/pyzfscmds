from setuptools import setup, find_packages
from os.path import abspath, dirname, join
from subprocess import call

from pyzfsutils import __version__

tests_require = [
    'coverage',
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'pytest-runner',
    'tox',
]

dev_require = [
    'Sphinx'
]


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='pyzfsutils',
    version=__version__,
    description='ZFS CLI Function Wrapper',
    long_description=readme(),
    url='http://github.com/johnramsden/pyzfsutils',
    author='John Ramsden',
    author_email='johnramsden@riseup.net',
    license='BSD-3-Clause',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python :: 3.6',
    ],
    keywords='cli',
    packages=find_packages(),
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev': dev_require,
    },
    zip_safe=False,
)
