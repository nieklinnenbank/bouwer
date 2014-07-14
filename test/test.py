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

import sys
import os.path
import inspect
import unittest
import bouwer.cli
from bouwer.config import *

class BouwerTester(unittest.TestCase):
    """
    Base test class for Bouwer
    """

    def setUp(self):
        """ Runs before each test """

        # Find our own location
        curfile = os.path.abspath(inspect.getfile(inspect.currentframe()))
        curdir  = os.path.dirname(curfile)

        # Determine paths
        self.rootdir = os.path.normpath(curdir + os.sep + '..')
        self.srcdir  = os.path.normpath(self.rootdir + os.sep + 'source')
        self.demodir = os.path.normpath(self.rootdir + os.sep + 'demo')
        self.bouwer  = os.path.normpath(self.rootdir + os.sep + 'bouw')

        # We need this to import generate.py's
        sys.path.insert(0, '.')
        sys.path.insert(1, self.srcdir)

class ConfTester(BouwerTester):
    """
    Tester class for the configuration layer
    """

    def setUp(self):
        """ Runs before each test case """

        # Create commmand line object
        sys.argv = [ "bouw", "--quiet" ]
        self.cli = bouwer.cli.CommandLine()
        
        # Reload configuration
        Configuration.Destroy()
        self.conf = Configuration.Instance(self.cli)

    def tearDown(self):
        """ Runs after each test case """
        Configuration.Destroy()

