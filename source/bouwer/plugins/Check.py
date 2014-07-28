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
import bouwer.util
from bouwer.plugin import *
from bouwer.builder import *
from bouwer.config import ConfigBool

class CheckOS(Plugin):
    """
    Check for the target OS.
    """

    def config_action_output(self):
        return [ 'CHECK' ]

    def initialize(self):
        self.os_dict = {
            'linux'  : 'LINUX',
            'win'    : 'WINDOWS',
            'cynwin' : 'CYGWIN',
            'darwin' : 'MACOS',
            'freebsd': 'FREEBSD',
            'sunos'  : 'SUNOS',
            'beos'   : 'BEOS',
            'aix'    : 'AIX',
            'netware': 'NETWARE'
        }

    def execute_config_params(self, conf):
        os_file = bouwer.util.tempfile(self.__class__.__name__ + '.' + conf.name)

        self.build.action(TargetPath(os_file), [],
                         '# CheckOS',
                          pretty_name='Checking for',
                          pretty_target='Operating System',#conf.name,
                          confitem=conf)

    def action_event(self, action, event):
        """
        Called when an Action has finished
        """
        # TODO: this is not parallel. Python function should be used
        #       so it can be parallel. But the python function should be
        #       able to modify the Config object. We need threads for parallizing
        #       with python functions then.

        # Update the configuration item
        if event.type == ActionEvent.FINISH:
            open(action.target, 'w').close()
            item = action.tags['confitem']

            for os in self.os_dict:
                if sys.platform.startswith(os):
                    item.update(self.os_dict[os])
                    break

            action.tags['pretty_target'] += ' ... ' + item.value()
