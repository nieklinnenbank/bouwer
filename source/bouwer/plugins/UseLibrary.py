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

from CCompiler import CCompiler
from bouwer.plugin import Plugin

class UseLibrary(Plugin):
    """
    Build and link against a library
    """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'LIBRARIES', 'OBJECTS' ]

    def config_output(self):
        """ Configuration output items """
        return [ 'LINK_LIBRARIES' ]

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
        CCompiler.Instance().generate_library_override(libraries)
