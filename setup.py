#!/usr/bin/env python
import os
import sys
import shutil
import unittest
from distutils.core import setup, Command
from numpy.distutils.misc_util import get_numpy_include_dirs

packages = ['cxroots', 'cxroots.tests']

# get the version
exec(open('cxroots/version.py').read())

# read the README_pip.rst
try:
    with open('README_pip.rst') as file:
        long_description = file.read()
except:
    long_description = None

setup(
    name = 'cxroots',
    version = __version__,
    description = 'Find all the roots (zeros) of a complex analytic function within a given contour in the complex plane.',
    long_description = long_description,
    author = 'Robert Parini',
    author_email = 'rp910@york.ac.uk',
    url = 'https://rparini.github.io/cxroots/',
    license = 'BSD',
    data_files = [("", ["LICENSE"])],
    packages = packages,
    platforms = ['all'],
    dependency_links=['git+git://github.com/pbrod/numdifftools@406a79877e0dd45aefe210b08e73cdd58ff4cb15#egg=numdifftools'],
    install_requires = ['pytest-runner', 'numpy', 'scipy', 'docrep', 'mpmath', 'numdifftools'],
    tests_require=['pytest'],
    keywords='roots zeros complex analytic functions',
    classifiers=[
	    'Development Status :: 4 - Beta',
	    'Intended Audience :: Science/Research',
	    'Topic :: Scientific/Engineering :: Mathematics',
	    'License :: OSI Approved :: BSD License',
	    'Programming Language :: Python :: 2.7',
	    'Programming Language :: Python :: 3',
	],
)
