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
import fcntl, termios, struct
from bouwer.plugin import Plugin
from bouwer.action import ActionEvent

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

    def action_event(self, action, event):
        """
        Called when an :class:`.ActionEvent` is triggered
        """
        if event.type == ActionEvent.FINISH:
            todo  = len(self.build.actions.workers.pending) + len(self.build.actions.workers.running)
            total = len(self.build.actions.actions)
            perc  = float(total - todo) / float(total)
            self.update_progress(perc, action.target)

    def get_console_width(self):
        """
        Return the width of the console in characters
        """
        # TODO: not portable to windows
        try:
            term = os.get_terminal_size()
            return term.columns
        except:
            try:
                return os.environ['COLUMNS']
            except:
                hw = struct.unpack('hh', fcntl.ioctl(1, termios.TIOCGWINSZ, '1234'))
                return hw[1]

    def update_progress(self, progress, label = ""):
        """
        Displays or updates a console progress bar
        """
        labelLength = len(label) + 16
        barLength   = self.get_console_width() - labelLength
        block       = int(round(barLength*progress))
        #text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, label)

        text = "\r[{0}] {1:.2%} {2}".format("#" * block + "-" * (barLength - block),
                                             progress,
                                             label)
        sys.stdout.write(text)
        sys.stdout.flush()

        if progress == 1.0:
            print()
