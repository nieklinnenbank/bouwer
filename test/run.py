#!/usr/bin/python
#
# Copyright (C) 2012 Niek Linnenbank
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import inspect
import unittest

class MyTestResult(unittest.TextTestResult):
    def getDescription(self, test):
        return str(test)

# TODO: this only allows me to select a testfile, not a testcase or class
if len(sys.argv) > 1:
    match = sys.argv[1]
else:
    match = 'test_*.py'

# Find our own location
curfile = os.path.abspath(inspect.getfile(inspect.currentframe()))
curdir  = os.path.normpath(os.path.dirname(curfile))

# Determine paths
rootdir = os.path.normpath(curdir + os.sep + '..')
srcdir  = os.path.normpath(rootdir + os.sep + 'source')

# We need this to import bouwer and test code
sys.path.insert(0, curdir)
sys.path.insert(1, srcdir)

# Startup the unit tests
suite  = unittest.TestLoader().discover('.', match)
runner = unittest.TextTestRunner(verbosity=2)
runner.resultclass = MyTestResult
runner.run(suite)


