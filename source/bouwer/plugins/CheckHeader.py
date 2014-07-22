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
from bouwer.plugin import *
from bouwer.builder import *
import bouwer.util
from CCompiler import CCompiler

class CheckHeader(Plugin):
    """
    See if a C header exists.
    """

    def config_input(self):
        return [ 'CC' ]

    def config_action_output(self):
        return [ 'CHECK' ]

    def execute_config(self, conf, header, is_required = False):

        # Generate C file, if not yet done already.
        # TODO: generic directory for putting these files please.
        cfile = bouwer.util.tempfile(self.__class__.__name__ + '.' + conf.name + '.c')

        # TODO: these must be cleaned up too. If in the generic directory, we can simply remove the directory....
        if not os.path.isfile(cfile):
            fp = open(cfile, 'w')
            fp.write('#include "' + header + '"\nint main(void) { return 0; }')
            fp.close()

        # Schedule Action to compile it
        CCompiler.Instance().c_object(SourcePath(cfile),
                          confitem=conf, filename=header,
                          pretty_name='CHECK', pretty_target=header,
                          required=is_required, quiet=True)

    def action_event(self, action, event):
        """
        Called when an Action has finished
        """

        item = action.tags['confitem']

        # Update the configuration item
        if event.type == ActionEvent.FINISH and event.result != 0:
            if action.tags['required']:
                self.log.error('C Header ' + action.tags['filename'] + ' not installed')
                sys.exit(1)
            else:
                item.update(False)
        else:
            item.update(True)

        action.tags['pretty_target'] += ' ... ' + str(item.value())
