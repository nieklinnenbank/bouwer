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
from bouwer.plugin import Plugin
from bouwer.config import ConfigBool, Config
from bouwer.builder import TargetPath

class UseLibrary(Plugin):
    """
    Build and link against a library
    """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'LIBRARIES' ]

    def config_output(self):
        """ Configuration output items """
        return [ 'LINK_LIBRARIES' ]

    def execute_before(self):
        """
        List of builders which must be executed first
        """
        return [ 'Library' ]

    def execute_config_params(self, item, libsrc):
        if item.value():
            self.execute_any(libsrc)

    def execute_any(self, libraries):
        """
        Build against a :py:`list` of `libraries`

        The library target for linking will be discovered by
        searching the generated :class:`.Action` objects in
        the actions layer.
        """

        # TODO: this should become a *TEMPORARY* per-directory override instead
        chain = self.conf.get('CC')
        cc    = self.conf.get(chain.value())

        # TODO: find the correct libary path using the actions layer!!!
        # TODO: only do it like this if static linking!!!
        # TODO: use keyword indirection instead of copying the original keywords?!
        tmp = ConfigBool(cc.name, **cc.keywords)
        slist = []

        libs = self.conf.get('LIBRARIES')
        if libs is None:
            return
        
        libdict = libs.value()

        # Loop all given libraries
        for lib in libraries:

            target, path = libdict[lib]
            slist.append(target)

            if lib[:3] == 'lib':
                libname = lib[3:]
            else:
                libname = lib
            tmp.keywords['ldpath'].append(os.path.dirname(target.absolute))
            tmp.keywords['incpath'].append(path)
            tmp.keywords['ldflags'] += ' -l' + libname + ' '

        self.conf.active_tree.add(tmp)
        self.conf.active_tree.add(Config('SOURCES', slist, temporary = True))
 
        """
        With this Library() instance, we can append e.g. libinc = 'include' or libinc='.'
        to automatically append an -I path for each Library():

           -I ./lib/fuzzors/libfuzz1 or -I ./lib/fuzzors/libfuzz1/include

        If all headers are in a central location and not per-library, the user can simply put it in the incpath=['include']:

           -I ./include
        """

