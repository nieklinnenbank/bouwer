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
from bouwer.config import *

##
# Build an executable program
#
class Program(Plugin):

    ##
    # Build an executable program
    #
    # @param target Name of the executable or Config item
    # @param sources List of source files of the program
    #
    def execute(self, target, sources):

        if type(target) is Config:
            prog = target.name.lower()
        elif type(target) is str:
            prog = target
        else:
            return

        # Make a list of objects on which we depend
        objects = []

        # Traverse all source files given
        for src in sources:
            objects.append(self.Object(src))

        # Retrieve compiler chain
        chain = self.get_item('CC')
        cc    = self.get_item(chain.value())                

        # TODO: use BUILDROOT, BUILDPATH

        # Link the program
        self.action(prog,
                    objects,
                    cc.keywords.get('cc') + ' ' + prog + ' ' + (' '.join(objects)))

        #self.env.register_action(target,
        #                         self.env['ld'] + ' ' + self.env['ldscript'] + ' '
        #                        + self.env['ldflags'], objects, "LD")
