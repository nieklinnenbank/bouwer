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

class ConfigTester(ConfTester):
    """
    Tests for the generic :class:`.Config` configuration item
    """

    def setUp(self):
        super(ConfigTester, self).setUp()
        self.item1 = Config('TESTITEM',
                             True,
                             'DEFAULT',
                             key1=True, key2='text', key3=['a', 'b', 'c'])

    def test_keyword_non_existing(self):
        """ Try to retrieve non-existing keyword """
        self.assertRaises(KeyError, self.item1.__getitem__, 'nonexisting')

    def test_keyword_getitem(self):
        """ Try to retrieve a valid keyword """
        self.assertEqual(self.item1['key1'], True)
        self.assertEqual(self.item1['key2'], 'text')
        self.assertEqual(self.item1['key3'], ['a', 'b', 'c'])

