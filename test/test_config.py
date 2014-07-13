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

import common
import bouwer.cli
from bouwer.config import *

class ConfigTester(common.BouwerTester):
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

class ConfigurationTester(ConfigTester):
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

        item1 = Config('TEST_ITEM1', 123)
        item2 = Config('TEST_ITEM2', 456)

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
        self.conf.put(item1)
        self.conf.put(item2)
        self.assertEquals(self.conf.get(item2.name), item2)
        self.assertNotEqual(self.conf.get(item2.name), item1)

    def test_put_override(self):
        """ Override a configuration item in a specific directory """

        item1 = Config('TEST_ITEM', 123)
        item2 = Config('TEST_ITEM', 456)
        
        # Put item1 in the default tree.
        self.conf.put(item1)
        self.assertEquals(self.conf.get(item1.name), item1)

        # Override item1 in some sub directory only
        self.conf.active_dir = './test/directory'
        self.conf.put(item2)
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

class ConfigTreeTester(ConfigTester):
    """
    Tests for the :class:`.ConfigTree` configuration item
    """

    def test_inherit(self):
        """ ConfigTree's should inherit items from the default tree """

        tree1 = ConfigTree('TREE1', True)
        tree2 = ConfigTree('TREE2', True)

        self.conf.put(tree1)
        self.conf.put(tree2)

        self.assertIsNone(self.conf.get('NON_EXISTING_ITEM'))
        self.assertIsInstance(self.conf.get('GCC'), ConfigBool)
        self.assertEqual(self.conf.get('GCC').name, 'GCC')

        self.assertIsNone(self.conf.get('NON_EXISTING_ITEM'))
        self.assertIsInstance(self.conf.get('GCC'), ConfigBool)
        self.assertEqual(self.conf.get('GCC').name, 'GCC')

    def test_value(self):
        """ Retrieve ConfigTree value """
        
        tree1 = ConfigTree('TREE1', True)
        tree2 = ConfigTree('TREE2', True)
        tree3 = ConfigTree('TREE3', False)

        self.conf.put(tree1)
        self.conf.put(tree2)
        self.conf.put(tree3)

        # See that the ConfigTree values are correct when
        # the default tree is active.
        self.conf.active_tree = self.conf.trees['DEFAULT']
        self.assertTrue(self.conf.get('DEFAULT').value())
        self.assertFalse(self.conf.get('TREE1').value())
        self.assertFalse(self.conf.get('TREE2').value())
        self.assertFalse(self.conf.get('TREE3').value())

        # Verify that the ConfigTree values are correct
        # when a custom configuration tree is active
        self.conf.active_tree = self.conf.trees['TREE1']
        self.assertTrue(self.conf.get('TREE1').value())
        self.assertFalse(self.conf.get('DEFAULT').value())
        self.assertFalse(self.conf.get('TREE2').value())
        self.assertFalse(self.conf.get('TREE3').value())

class ConfigListTester(ConfigTester):
    
    def test_override_add_items(self):
        self.skipTest('implement')
    
    def test_override_change_items(self):
        self.skipTest('implement')

    def test_override_remove_items(self):
        self.skipTest('implement')


