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

    def _private_func(self):
        print("Private function")

    def execute(self, target, sources):
        print("Building Library `" + target + "' from `" + str(sources) + "'")
        print("I'm executed from `" + self.env.bouwfile + "'")
        self._private_func()

    # TODO: add '#include' implicit dependencies
    # TODO: decide here with timestamps if we need to redo this action

        for src in sources:
            splitfile = os.path.splitext(src)
            print(str(splitfile))
#        outfile = os.path.splitext(src)[0] + '.o'
#        self.register_action(outfile, self['cc'] + ' ' + self['ccflags'] + ' ' + outfile + ' ' + srcfile)

#        self.register_action(target, self['ar'] + ' ' + self['arflags'] + ' ' + target + ' ' + str(sources),
#                             sources)

#        n = len(sources) + 1
#        i = 1
#
#        for src in sources:
#            #print(self['cc'] + ' ' + self['ccflags'] + ' -c -o ' + src + '.o ' +  src)
#            print('[' + str(i) + '/' + str(n) + ']  CC  ' + src)
#            i = i + 1
#
#        print('[' + str(n) + '/' + str(n) + ']  AR  ' + target)
