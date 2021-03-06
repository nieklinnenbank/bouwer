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

"""
Bouwer unit tester main entry
"""

import os
import sys
import inspect
import unittest

class MyTestResult(unittest.TextTestResult):
    """
    Result class that prints a textual description of the test
    """
    def getDescription(self, test):
        return str(test)

# Find our own location
curfile = os.path.abspath(inspect.getfile(inspect.currentframe()))
curdir  = os.path.normpath(os.path.dirname(curfile))

# Determine paths
rootdir = os.path.normpath(curdir + os.sep + '..')
srcdir  = os.path.normpath(rootdir + os.sep + 'source')
plugdir = os.path.normpath(rootdir + os.sep + 'source' + os.sep + 'bouwer' + os.sep + 'plugins')

# We need this to import bouwer and test code
if curdir not in sys.path:
    sys.path.insert(0, curdir)
if srcdir not in sys.path:
    sys.path.insert(1, srcdir)
if plugdir not in sys.path:
    sys.path.insert(2, plugdir)

# Retrieve tests to be executed
if len(sys.argv) > 1:
    suite = unittest.TestLoader().loadTestsFromName(sys.argv[1])
else:
    suite  = unittest.TestLoader().discover('.', 'test_*.py')

# Startup the unit tests
runner = unittest.TextTestRunner(verbosity=2)
runner.resultclass = MyTestResult
runner.run(suite)

