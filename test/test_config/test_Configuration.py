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
Bouwer configuration layer tests
"""

from test import *
from bouwer.config import *

class ConfigurationTester(ConfTester):
    """
    Tests for the :class:`.Configuration` class.
    """

    def test_get(self):
        """ Retrieve a configuration item """
        self.assertIsNone(self.conf.get('NON_EXISTING_ITEM'))
        self.assertIsInstance(self.conf.get('GCC'), ConfigBool)
        self.assertEqual(self.conf.get('GCC').name, 'GCC')

    def test_put_default(self):
        """ Store a configuration item in the default tree """

        item1 = Config('TEST_ITEM1', 123, '.')
        item2 = Config('TEST_ITEM2', 456, '.')

        # Test insert items to the default tree
        self.conf.put(item1)
        self.assertEquals(self.conf.get(item1.name), item1)
        self.conf.put(item2)
        self.assertEquals(self.conf.get(item2.name), item2)

    def test_put_overwrite(self):
        """ Overwrite a configuration item """

        item1 = Config('TEST_ITEM', 123)
        item2 = Config('TEST_ITEM', 456)

        # Try to insert an item with the same name and directory
        self.conf.put(item1, path = '.')
        self.conf.put(item2, path = './subdir')
        self.conf.active_dir = './subdir'
        self.assertEquals(self.conf.get(item2.name), item2)
        self.assertNotEqual(self.conf.get(item2.name), item1)

    def test_put_override(self):
        """ Override a configuration item in a specific directory """

        item1 = Config('TEST_ITEM', 123)
        item2 = Config('TEST_ITEM', 456)

        # Put item1 in the default tree.
        self.conf.put(item1, path = '.')
        self.assertEquals(self.conf.get(item1.name), item1)

        # Override item1 in some sub directory only
        self.conf.active_dir = './test/directory'
        self.conf.put(item2, path = './test/directory')
        self.assertEquals(self.conf.get(item2.name), item2)
        self.assertNotEqual(self.conf.get(item1.name), item1)

        # Also a sub sub directory should give item2
        self.conf.active_dir = './test/directory/sub/dir'
        self.assertEquals(self.conf.get(item2.name), item2)
        self.assertNotEqual(self.conf.get(item1.name), item1)

        # Switching back to top level should still give item1
        self.conf.active_dir = self.conf.base_conf
        self.assertEquals(self.conf.get(item1.name), item1)

    def test_put_override_tree(self):
        """ Override a configuration item in a specific tree and directory """
        self.skipTest('implement')

    def test_load(self):
        self.skipTest('implement')

    def test_save(self):
        self.skipTest('implement')
    
    def test_reset(self):
        self.skipTest('implement')


