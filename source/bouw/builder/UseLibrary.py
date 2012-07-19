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
# Build and link against a library
#
class UseLibrary:

    ##
    # Constructor
    #
    def __init__(self, env):
        self.env = env

    ##
    # Build and link against a library
    #
    # @param libraries List of library names
    #
    def execute(self, libraries):

        for lib in libraries:

            # Find the correct include parameter for ccflags
            inc_param = self.env['incflags'].replace('%INCLUDE%', 'library' + os.sep + lib)

            # TODO: this is ugly, find some clearer way to extend the Config object

            # Append library include paths to the C compiler flags
            self.env.config.set(self.env['id'], 'ccflags',
                self.env['ccflags'] + ' ' + inc_param)
