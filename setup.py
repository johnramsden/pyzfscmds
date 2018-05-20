from setuptools import setup, find_packages
import subprocess

from pyzfscmds import __version__

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


def vcs_release(version: str):
    return version + '+git.' + subprocess.check_output(
                                    ['git', 'rev-parse', '--short', 'HEAD'],
                                    universal_newlines=True, stderr=subprocess.PIPE)


setup(
    name='pyzfscmds',
    version=__version__,
    description='ZFS CLI Command Wrapper Library',
    long_description=readme(),
    url='http://github.com/johnramsden/pyzfscmds',
    author='John Ramsden',
    author_email='johnramsden@riseup.net',
    license='BSD-3-Clause',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python :: 3.6',
    ],
    keywords='library',
    packages=find_packages(exclude=["*tests*", "test_*"]),
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev': dev_require,
    },
    zip_safe=False,
)
