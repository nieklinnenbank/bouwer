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
import os.path
from bouwer.plugin import *

class ConfigHeader(Plugin):
    """
    Output a C header file with :class:`.Configuration` encoded as #define's
    """

    def inspect(self, conf):
        """ Decide if we agree with the given configuration """
        pass

    def execute_any(self, filename):
        """ Builder implementation for ConfigHeader() """
        self.conf.write_header(filename)

