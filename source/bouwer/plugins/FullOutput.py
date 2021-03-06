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
# Output the full command of each Action
#
class FullOutput(Plugin):

    ##
    # Initialize plugin
    #
    def initialize(self):
        self.conf.cli.parser.add_argument('--full',
            dest    = 'output_plugin',
            action  = 'store_const',
            const   = self,
            default = argparse.SUPPRESS,
            help    = 'Output full commands for each action')

    ##
    # Called just before the Action is executed by the worker.
    #
    def action_event(self, action, event):
        if event.type == ActionEvent.FINISH:
            print(str(event.worker) + ' : ' + str(action.command))
