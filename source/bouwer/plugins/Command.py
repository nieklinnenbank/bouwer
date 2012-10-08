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
from bouwer.config import *

##
# Run a shell command
#
class Command(Plugin):

    ##
    # Run a shell command
    #
    # @param cmd The command to run
    # @param item Optional configuration item or None.
    #
    def execute_any(self, cmd, item = False):

        if (type(item) is Config and item.value) or item is False:
            os.system(cmd)
        # self.build.generate_action(...)
        # os.system(cmd)
