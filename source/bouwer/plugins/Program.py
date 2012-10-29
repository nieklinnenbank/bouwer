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
import glob
from bouwer.plugin import *
from bouwer.builder import *

class Program(Plugin):
    """
    Build an executable program
    """

    def execute_config(self, item, sources):
        """
        Build a program given a :class:`.Config` `item` and `sources` list.
        """
        # TODO: also support the program = keyword, like library =
        if item.value():
            self.execute_target(TargetPath(item.name.lower()), sources)

    def execute_target(self, target, sources):
        """
        Build an program given its `target` name and `sources` list
        """

        # Make a list of objects on which we depend
        # TODO: problem: what if there is never any UseLibrary which publishes this???
        try:
            extra = self.build.get('sources')
        except KeyError:
            extra = []
        objects = []

        # TODO: make the actions a TRANSACTION, so that they will be forgotten
        # if this builder was delayed...

        # Traverse all source files given
        for src in sources:
            objects.append(self.Object(src))

        # Retrieve compiler chain
        chain = self.get_item('CC')
        cc    = self.get_item(chain.value())

        # Add linker paths
        ldpath = ''
        for path in cc.keywords.get('ldpath'):
            ldpath += cc.keywords.get('ldflag') + path + ' '

        # Link the program
        self.action(target,
                    objects + extra, 
                    cc.keywords.get('ld') + ' ' + str(target) + ' ' +
                    (' '.join([str(o) for o in objects])) + ' ' + ldpath +
                    cc.keywords.get('ldflags'))

