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

##
# Build an executable object
#
class Object(Plugin):

    ##
    # Detect a valid compiler configuration
    #
    def inspect(self, conf):
        # Todo: attempt to compile a C program with this config
        pass

    ##
    # Build an executable Object
    #
    # @param source Source file
    #
    def execute(self, source):

        # Retrieve C compiler configuration.
        chain = self.get_item('CC')
        cc    = self.get_item(chain.value())

        # TODO: add '#include' implicit dependencies
        splitfile = os.path.splitext(source)

        # Compile a C source file into an object file
        if splitfile[1] == '.c':

            # Output file is the name with the .o suffix
            outfile = splitfile[0] + '.o'

            # Register compile action
            self.action(outfile,
                        [ source ],
                        cc.keywords.get('cc') + ' ' + outfile + ' ' + cc.keywords.get('ccflags') + ' ' + source)

            # Success
            return outfile

        # Unknown filetype
        else:
            raise Exception('unknown filetype: ' + source)
