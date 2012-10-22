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

import common
import bouwer.util

class DummySingleton1(bouwer.util.Singleton):
    """ First Dummy Singleton class """

    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

class DummySingleton2(bouwer.util.Singleton):
    """ Second Dummy Singleton class """

    def __init__(self, arg1, arg2, arg3):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

class SingletonTester(common.BouwerTester):
    """ Tests for the Bouwer command line interface """

    def setUp(self):
        """ Runs before each testcase """
        try:
            del DummySingleton1.__class_obj__
            DummySingleton1.__init__ = DummySingleton1.__orig_init__
        except:
            pass

        try:
            del DummySingleton2.__class_obj__
            DummySingleton2.__init__ = DummySingleton2.__orig_init__
        except:
            pass

    def test_single(self):
        """ Verify that Singleton has one instance maximum """
        dummy1 = DummySingleton1.Instance("a", "b")
        dummy2 = DummySingleton1.Instance()
        dummy3 = DummySingleton1.Instance()

        self.assertEquals(dummy1, dummy2,
                         'Singleton.Instance() must return the same instance')
        self.assertEquals(dummy1, dummy3,
                         'Singleton.Instance() must return the same instance')
        self.assertEquals(id(dummy1), id(dummy2),
                         'Singleton.Instance() must return the same instance')
        self.assertEquals(id(dummy1), id(dummy3),
                         'Singleton.Instance() must return the same instance')

    def test_unique(self):
        """ Verify that Singleton produces a unique instance per class """
        dummy1 = DummySingleton1.Instance("a", "b")
        dummy2 = DummySingleton2.Instance("a", "b", "c")

        self.assertNotEqual(dummy1, dummy2,
                           'Singleton.Instance() must return unique instance per class')
        self.assertNotEqual(id(dummy1), id(dummy2),
                           'Singleton.Instance() msut return unique instance per class')

    def test_init(self):
        """ Verify that Singletons can only be initialized once """
        dummy1 = DummySingleton1.Instance("a", "b")

        self.assertRaises(Exception, DummySingleton1.Instance, "a", "b")

