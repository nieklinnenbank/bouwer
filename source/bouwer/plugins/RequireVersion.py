#
# Copyright (C) 2014 Niek Linnenbank
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
import os.path
import random
from bouwer.config import *
from bouwer.builder import *
from bouwer.plugin import *
from bouwer.cli import CommandLine

class RequireVersion(Plugin):
    """
    Verify that Bouwer has the given minimum/maximum version.
    """

    def execute_any(self, minimum, maximum='9.9.9'):
        """ Builder implementation """

        cur_v = CommandLine.Instance().VERSION.split('.')
        min_v = minimum.split('.')
        max_v = maximum.split('.')

        for i in range(0, 2):
            if not (int(cur_v[i]) >= int(min_v[i]) and int(cur_v[i]) <= int(max_v[i])):
                self.log.error('Incompatible Bouwer version ' + CommandLine.Instance().VERSION + \
                               ' (min=' + str(minimum) + ' max=' + str(maximum) + ')')
                sys.exit(1)
