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
# Build a static library
#
class Library:

    ##
    # Constructor
    #
    def __init__(self, env):
        self.env = env

    ##
    # Build a static library
    #
    # @param target Name of the library to build
    # @param sources List of source files of the library
    #
    def execute(self, target, sources):

        # Make a list of objects on which we depend
        objects = []

        # Traverse all source files given
        for src in sources:
            objects.append(self.env.Object(src))

        # Create the archive after all objects are done
        self.env.register_action(target + '.a',
                                 self.env['ar'] + ' ' + self.env['arflags'],
                                 objects, "AR")
