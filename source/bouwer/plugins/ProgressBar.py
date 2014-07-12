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

import argparse
import progressbar
from bouwer.plugin import Plugin

class ProgressBar(Plugin):
    """
    Output a textual progress bar on the terminal
    """

    def initialize(self):
        """
        Initialize plugin
        """
        self.conf.cli.parser.add_argument('-p', '--progress',
            dest    = 'output_plugin',
            action  = 'store_const',
            const   = self,
            default = argparse.SUPPRESS,
            help    = 'Output a progress bar to indicate action status')

        self.bar = progressbar.ProgressBar('blue')

    def action_event(self, action, event):
        """
        Called when an :class:`.ActionEvent` is triggered
        """
        todo  = len(self.build.actions.pending) + len(self.build.actions.running)
        done  = len(self.build.actions.finished)
        perc  = (done / (todo + done)) * 100
        
        self.bar.render(perc, action.target)
