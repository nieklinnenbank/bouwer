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
from CCompiler import CCompiler
from bouwer.plugin import *
from bouwer.config import *
from bouwer.builder import *

class Library(Plugin):
    """ Build a software library """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'CHECK', 'CONFIG', 'LIBRARY_OBJECTS' ]

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
        CCompiler.Instance().c_library(TargetPath(target), sources, item)

    def execute_target(self, target, sources):
        """
        Build a library using a `target` name and list of `sources`
        """
        CCompiler.Instance().c_library(target, sources)

