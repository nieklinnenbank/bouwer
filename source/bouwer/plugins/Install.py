#
# Copyright (C) 2014 Niek Linnenbank
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
import random
import sys
import tarfile
from bouwer.config import *
from bouwer.builder import *
from bouwer.plugin import *

class Install(Plugin):
    """
    Copy files to a new location
    """

    def execute_any(self, stritem_dir, files):
        """ Builder implementation """

        # If a prefix is configured, add it.
        if self.conf.get('PREFIX'):
            prefix = self.conf.get('PREFIX').value()
        else:
            prefix = ''

        # Schedule Action to compile it
        for f in files:
            path = TargetPath('')
            path.absolute = prefix + str(stritem_dir) + '/' + os.path.basename(f)

            self.build.action(path, [SourcePath(f)],
                              self.action_run,
                              pretty_name='COPY',
                              pretty_target=f + ' -> ' + path.absolute)

    def action_run(self, action):
        """
        Run the given action
        """
        try:
            shutil.copy(action.sources[0], action.target)
        except IOError as e:
            print(e)
            return 1
        return 0
