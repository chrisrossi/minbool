##############################################################################
#
# Copyright (c) 2008-2011 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    ]

tests_require = [
    ]

if sys.version_info < (2, 7, 0, 0):
    tests_require.append('unittest2')

testing_extras = tests_require + ['nose', 'coverage']

setup(name='minbool',
      version='1.0',
      description=('Implementation of Quine-McCluskey algorithm for minimizing '
                   'boolean expressions.'),
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
      author="Chris Rossi",
      author_email="chris@archimedeanco.com",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      extras_require = {
          'testing':testing_extras,
          },
      tests_require = tests_require,
      test_suite="minbool.tests",
      entry_points = """\
      [console_scripts]
      simplify = minbool:main
      """
      )

