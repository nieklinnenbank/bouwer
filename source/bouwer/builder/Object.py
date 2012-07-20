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
# Build an executable object
#
class Object:

    ##
    # Constructor
    #
    def __init__(self, env):
        self.env = env

    ##
    # Build an executable Object
    #
    # @param source Source file
    #
    def execute(self, source):

        # TODO: add '#include' implicit dependencies
        # TODO: decide here with timestamps if we need to redo this action
        splitfile = os.path.splitext(source)

        # Compile a C source file into an object file
        if splitfile[1] == '.c':

            # Output file is the name with the .o suffix
            outfile = splitfile[0] + '.o'

            # Register compile action
            self.env.register_action(outfile,
                                     self.env['cc'] + ' ' + self.env['ccflags'],
                                     [source],
                                     "CC")
            return outfile

        # Unknown filetype
        else:
            raise Exception('unknown filetype: ' + source)
