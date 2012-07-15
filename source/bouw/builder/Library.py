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
# @param target Destination library file to build
# @param sources List of source code files to include
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

        # TODO: add '#include' implicit dependencies
        # TODO: decide here with timestamps if we need to redo this action

        objects = []

        # Traverse all source files given
        for src in sources:
            splitfile = os.path.splitext(src)

            # Compile a C source file into an object file
            if splitfile[1] == '.c':

                # Output file is the name with the .o suffix
                outfile = splitfile[0] + '.o'
                objects.append(outfile)

                # Register compile action
                self.env.register_action(outfile,
                                         self.env['cc'] + ' ' + self.env['ccflags'],
                                         [src])

            # Unknown filetype
            else:
                raise Exception('unknown filetype: ' + src)

        # Create the archive after all objects are done
        self.env.register_action(target + '.a',
                                 self.env['ar'] + ' ' + self.env['arflags'],
                                 objects)

        # TODO: almost.. here please specify the path to the _buildroot_ objects

#        n = len(sources) + 1
#        i = 1
#
#        for src in sources:
#            #print(self['cc'] + ' ' + self['ccflags'] + ' -c -o ' + src + '.o ' +  src)
#            print('[' + str(i) + '/' + str(n) + ']  CC  ' + src)
#            i = i + 1
#
#        print('[' + str(n) + '/' + str(n) + ']  AR  ' + target)
