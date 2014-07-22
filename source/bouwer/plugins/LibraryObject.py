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

from bouwer.plugin import Plugin
from CCompiler import CCompiler

class LibraryObject(Plugin):
    """
    Specify an additional object for a library
    """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'CONFIG' ]

    def config_output(self):
        """ Configuration output items """
        return [ 'LIBRARY_OBJECTS' ]

    def execute_source(self, source):
        """
        Build an executable object given its `source` file
        """
        compiler.CCompiler.Instance().c_object(source)

    def execute_config(self, item, sources):
        """
        Build executable objects if configurion item `item` is True
        """
        if item.value():
            for source in sources:
                CCompiler.Instance().c_object(source, item)