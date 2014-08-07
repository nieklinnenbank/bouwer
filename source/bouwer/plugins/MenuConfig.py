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
import argparse
from bouwer.plugin import Plugin

class MenuConfig(Plugin):
    """
    Configure using the urwid / ncurses text-console frontend
    """

    def initialize(self):
        """
        Initialize the plugin
        """
        self.conf.cli.parser.add_argument('--menuconfig', dest='config_plugin',
            action='store_const', const=self, default=argparse.SUPPRESS,
            help='Change configuration using text console interface (urwid)')

    def configure(self, conf):
        """
        Configure using urwid
        """
        try:
            import urwid
        except:
            sys.exit('urwid python module not installed')

        for tree in conf.trees.values():
            for path, item_list in tree.get_items_by_path().items():
                print(path)

                for item in item_list:
                    print(item.name + ' = ' + str(item))

                print
