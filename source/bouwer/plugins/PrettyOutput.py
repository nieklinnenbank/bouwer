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
# Output prettyfied commands
#
class PrettyOutput(Plugin):

    ##
    # Initialize plugin
    #
    def initialize(self, conf):
        conf.cli.parser.add_argument('--pretty',
            dest    = 'output_plugin',
            action  = 'store_const',
            const   = self,
            default = argparse.SUPPRESS,
            help    = 'Output only the builder name and target of each action')

    def output(self, action, event, **tags):
        if event.event == 'execute':
            print('  Object  ' + str(action.target))
