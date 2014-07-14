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

class ConfigTreeTester(ConfTester):
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

