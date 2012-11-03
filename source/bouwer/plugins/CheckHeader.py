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

##
# Check if a configuration supports the given header file.
#
class CheckHeader:

    ##
    # Decide if we "agree" with the given configuration.
    #
    def inspect(self, conf):
        # Todo: attempt to compile a C program with this config.
        # Then modify the configuration based on if the header file exists and compiles
        pass

    def execute_any(self, filename):
        print("outputting header to " + str(filename))

