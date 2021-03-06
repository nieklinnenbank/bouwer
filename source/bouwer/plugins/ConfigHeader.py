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
import random
from bouwer.config import *
from bouwer.builder import *
from bouwer.plugin import *

class ConfigHeader(Plugin):
    """
    Output a C header file with :class:`.Configuration` encoded as #define's
    """

    def config_action_output(self):
        return [ 'CONFIG' ]

    def config_input(self):
        """ We can only write the config header when all items are final """
        return [ 'CHECK', 'CC' ]

    def execute_any(self, filename, prefix='CONFIG_'):
        """ Builder implementation for ConfigHeader() """

        # TODO: we should be able to provide a python function as builder also...
        target = TargetPath(filename)
        source = SourcePath('')
        source.absolute = '.bouwconf'

        # Schedule Action to compile it
        self.build.action(target, [ source ], '# ConfigHeader',
                          pretty_name='GEN',
                          pretty_target=target.absolute,
                          prefix=prefix)

    def action_event(self, action, event):
        """
        Called when an Action has finished
        """
        if event.type == ActionEvent.FINISH:

            splitfile = os.path.splitext(action.target)
            number = random.randint(100000, 999999)

            # Only C header files supported for now
            if splitfile[1] == '.h':

                # Open the header for writing
                self.outfile = open(action.target, 'w')

                # Write initial head info
                self.outfile.write('#ifndef __H_' + str(number) + '\n'
                                   '#define __H_' + str(number) + '\n\n') 

                # Current tree.
                self._write_c_header(self.conf.active_tree, action.tags['prefix'])

                # Also the default tree
                if self.conf.active_tree.name != 'DEFAULT':
                    self._write_c_header(self.conf.trees['DEFAULT'], action.tags['prefix'])

                self.outfile.write('#endif\n\n')
                self.outfile.close()

    def _write_c_header(self, item, prefix):
        """ Append item to a C header file """

        if isinstance(item, ConfigBool) and not item.value():
            self.outfile.write('/* ' + prefix + item.name + ' not set */\n')
        else:
            self.outfile.write('#define ' + prefix + item.name + ' ')

            if isinstance(item, ConfigBool):
                self.outfile.write('true\n')
            else:
                self.outfile.write('"' + str(item.value()) + '"\n')

        if isinstance(item, ConfigTree):
            for items in item.subitems.values():
                child_item = items[0]

                # Skip items that are overridden in the default tree.
                if item != self.conf.active_tree and child_item.name in self.conf.active_tree.subitems:
                    continue

                # Only take the first item. Not multiple overrides.
                self._write_c_header(child_item, prefix)
