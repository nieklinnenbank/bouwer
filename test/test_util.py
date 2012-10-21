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

class DummySingleton(bouwer.util.Singleton):
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

class SingletonTester(common.BouwerTester):
    """ Tests for the Bouwer command line interface """

    def test_single(self):
        """ Verify that Singleton has one instance maximum """
        dummy1 = DummySingleton.Instance("a", "b")
        dummy2 = DummySingleton.Instance()
        dummy3 = DummySingleton.Instance()

        self.assertEquals(dummy1, dummy2,
                         'Singleton.Instance() must return the same instance')
        self.assertEquals(dummy1, dummy3,
                         'Singleton.Instance() must return the same instance')
        self.assertEquals(id(dummy1), id(dummy2),
                         'Singleton.Instance() must return the same instance')
        self.assertEquals(id(dummy1), id(dummy3),
                         'Singleton.Instance() must return the same instance')

