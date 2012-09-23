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
import sys
import progressbar
from bouwer.plugin import *

##
# Output a progress bar to the terminal
#
class ProgressBar(Plugin):

    ##
    # Initialize plugin
    #
    def initialize(self, conf):
        conf.cli.parser.add_argument('-p', '--progress',
            dest    = 'output_plugin',
            action  = 'store_const',
            const   = self,
            default = argparse.SUPPRESS,
            help    = 'Output a progress bar to indicate action status')

        self.bar = progressbar.ProgressBar('blue')

    ##
    # See if we have all dependencies for this plugin
    #
    def exists(self):
        return True

    ##
    # Called just before the Action is executed by the worker.
    #
    # @param action The action to output
    # @param tags Optional statistical information of the status of the action.
    #
    def output(self, action, **tags):

#        if tags['stage'] == 'running':
            #bar = progressbar.ProgressBar("blue")
        if tags['stage'] == 'finished':
        
            todo  = tags['pending'] + tags['running']
            done  = tags['finished']
            perc  = (done / (todo + done)) * 100
        
            self.bar.render(perc, action.target)#, action.target)
