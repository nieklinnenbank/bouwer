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
        for src in sources:
            compiler.c_object(src)

        # Generate action for linking the library
        self.build.action(target, compiler.c_object_list,
                          cc['ar'] + ' ' +
                          cc['arflags'] + ' ' + str(target) + ' ' +
                        (' '.join([str(o) for o in compiler.c_object_list])))

        # Clear C object list
        compiler.c_object_list = []

        # Publish ourselves to the libraries list
        if self.conf.active_tree.get('LIBRARIES') is None:
            # TODO: why do i need to specify active_tree here...
            self.conf.active_tree.add(Config('LIBRARIES', {}, temporary = True),
                                      Configuration.Instance().base_conf) # TODO: path is an ugly hack...

        # Add ourselve to the libraries dictionary
        libdict = self.conf.get('LIBRARIES').value()
        libdict[libname] = (target, self.conf.active_dir)

