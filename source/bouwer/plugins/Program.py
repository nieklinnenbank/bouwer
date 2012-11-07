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
import compiler
from bouwer.plugin import *
from bouwer.builder import *

class Program(Plugin):
    """
    Build an executable program
    """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'LINK_LIBRARIES' ]

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

        # Retrieve compiler chain
        chain = self.conf.get('CC')
        cc    = self.conf.get(chain.value())
        objects = []

        try:
            extra = self.build.get('sources')
        except KeyError:
            extra = []

        # Traverse all source files given
        for source in sources:
            objects.append(compiler.c_object(source))

        # Add linker paths
        ldpath = ''
        for path in cc.keywords.get('ldpath'):
            ldpath += cc.keywords.get('ldflag') + path + ' '

        # Link the program
        self.build.action(target,
                          objects + extra, 
                          cc.keywords.get('ld') + ' ' + str(target) + ' ' +
                         (' '.join([str(o) for o in objects])) + ' ' + ldpath +
                          cc.keywords.get('ldflags'))

