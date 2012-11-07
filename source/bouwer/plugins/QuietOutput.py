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

class QuietOutput(Plugin):
    """
    Outputs nothing unless an error occurs
    """

    def initialize(self):
        """ Initialize plugin """
        self.conf.cli.parser.add_argument('-q', '--quiet',
            dest    = 'output_plugin',
            action  = 'store_const',
            const   = self,
            default = argparse.SUPPRESS,
            help    = 'Do not output anything unless an error occurs')

    def output(self, action, event, **tags):
        """ Does nothing for quiet """
        pass

