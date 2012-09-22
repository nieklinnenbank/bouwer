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
from bouwer.plugin import *

##
# Output a progress bar to the terminal
#
class ProgressBarOutput(Plugin):

    ##
    # Initialize plugin
    #
    def initialize(self, cli):
        pass

    ##
    # See if we have all dependencies for this plugin
    #
    def exists(self):
        return True

    ##
    # Output the current status of the action layer
    #
    # @param action The action which is about to begin executing
    # @param action_tree ActionTree instance
    #
    def output(self, action, action_tree):
        pass
