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
# Build an executable program
#
class Program:

    ##
    # Constructor
    #
    def __init__(self, env):
        self.env = env

    ##
    # Build an executable program
    #
    # @param target Name of the executable
    # @param sources List of source files of the program
    #
    def execute(self, target, sources):

        # Make a list of objects on which we depend
        objects = []

        # Traverse all source files given
        for src in sources:
            objects.append(self.env.Object(src))

        # Link the program
        self.env.register_action(target,
                                 self.env['ld'] + ' ' + self.env['ldscript'] + ' '
                                + self.env['ldflags'], objects, "LD")
