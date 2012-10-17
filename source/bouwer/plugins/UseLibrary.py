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
    # Build and link against a library
    #
    # @param libraries List of library names
    #
    def execute_any(self, libraries):

        # TODO: find the target library in the ActionTree
        # for each library, make sure it gets the right -L <path> and -l<name>
        # as a temporary per-directory override.
        # do the -L via search in the ActionTree.
        # we need to have the builder priority/ordering working for this...
        # also make sure to add libinc <path>, for includes
        pass

        #for lib in libraries:
        # Find the correct include parameter for ccflags
        #inc_param = self.env['incflags'].replace('%INCLUDE%', 'library' + os.sep + lib)
            
        #print('fixing library ' + lib[3:])
        #lib_param = self.env['libflags'].replace('%LIBRARY%', lib)
        #lib_param = lib_param.replace('%LIBNAME%', lib[3:])

        # TODO: this is ugly, find some clearer way to extend the Config object

        # Append library include paths to the C compiler flags
        #self.env.config.set(self.env['id'], 'ccflags',
        #    self.env['ccflags'] + ' ' + inc_param)

        # Append library linker flags
        #self.env.config.set(self.env['id'], 'ldflags',
        #    self.env['ldflags'] + ' ' + lib_param)

