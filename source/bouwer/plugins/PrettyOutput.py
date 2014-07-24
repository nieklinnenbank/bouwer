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
    def initialize(self):
        self.conf.cli.parser.add_argument('--pretty',
            dest    = 'output_plugin',
            action  = 'store_const',
            const   = self,
            default = self,
            help    = 'Output only the builder name and target of each action')

    def action_event(self, action, event):
        if event.type == ActionEvent.FINISH:

            if action.tags.get('pretty_skip', False):
                return

            if 'pretty_name' in action.tags:
                pretty_name = action.tags['pretty_name']
            else:
                pretty_name = str(action.builder.__class__.__name__)

            if 'pretty_target' in action.tags:
                pretty_target = action.tags['pretty_target']
            else:
                pretty_target = str(action.target)

            print(pretty_name.rjust(6) + '  ' + pretty_target)

