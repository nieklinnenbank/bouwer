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
import argparse
from bouwer.plugin import *

##
# Configure using ncurses
#
class MenuConfig(Plugin):

    ##
    # Initialize the plugin. Only called once if exists is True.
    #
    def initialize(self):
        self.conf.cli.parser.add_argument('--menuconfig', dest='config_plugin',
            action='store_const', const=self, default=argparse.SUPPRESS,
            help='Change configuration using ncurses terminal interface')

    ##
    # See if we have ncurses installed
    #
    def inspect(self, conf):
        # Look for the ncurses module
        return True

    ##
    # Runs the menu configuration
    #
    def configure(self, conf):
        pass


