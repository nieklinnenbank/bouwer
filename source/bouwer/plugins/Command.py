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
from bouwer.plugin import Plugin
from bouwer.builder import TargetPath, SourcePath

class Command(Plugin):
    """
    Run a shell command
    """

    def config_input(self):
        return [ 'CHECK', 'CONFIG' ]

    def execute_config(self, item, sources, command, outfile=None):
        """
        Runs a command only if item is True
        """
        if item.value():
            self.build.action(TargetPath(outfile), sources,
                              command,
                              pretty_name='CMD',
                              pretty_target=command)

    def execute_any(self, command):
        """ Run a shell command """
        os.system(command)
