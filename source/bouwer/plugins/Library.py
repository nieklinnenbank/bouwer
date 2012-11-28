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
import compiler
from bouwer.plugin import *
from bouwer.config import *
from bouwer.builder import *

class Library(Plugin):
    """ Build a software library """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC' ]

    def config_output(self):
        """ Configuration output items """
        return [ 'LIBRARIES' ]

    def execute_config(self, item, sources):
        """
        Build a library using a :class:`.Config` and list of `sources`
        """
        if not item.value():
            return

        target = item.get_key('library', item.name.lower())

        # Look for optional sources in our child config items
        # TODO: this is an ugly hack. Configuration layer should not be
        # aware of source/target files
        for child_name in item.get_key('childs', []):
            child = self.conf.get(child_name)

            if isinstance(child, ConfigBool) and child.value() and 'source' in child.keys():
                sources.append(SourcePath(child.get_key('source')))

        self.execute_target(TargetPath(target), sources)

    def execute_target(self, target, sources):
        """
        Build a library using a `target` name and list of `sources`
        """

        chain = self.conf.get('CC')
        cc = self.conf.get(chain.value())
        libname = str(target.relative)
        target.append('.a')

        # Generate actions to build the library objects
        objects = []
        for src in sources:
            objects.append(compiler.c_object(src))

        # Generate action for linking the library
        self.build.action(target, objects,
                          cc['ar'] + ' ' +
                          cc['arflags'] + ' ' + str(target) + ' ' +
                        (' '.join([str(o) for o in objects])))

        # Publish ourselves to the libraries list
        if self.conf.active_tree.get('LIBRARIES') is None:
            # TODO: why do i need to specify active_tree here...
            self.conf.active_tree.add(Config('LIBRARIES', {}, temporary = True))

        # Add ourselve to the libraries dictionary
        libdict = self.conf.get('LIBRARIES').value()
        libdict[libname] = (target, self.conf.active_dir)

