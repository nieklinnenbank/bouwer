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
from bouwer.config import ConfigBool
import bouwer.util
from CCompiler import CCompiler

class CheckFunction(Plugin):
    """
    See if a C function exists.
    """

    def config_input(self):
        return [ 'CC' ]

    def config_action_output(self):
        return [ 'CHECK' ]

    def execute_any(self, confname, function, lib, is_required = False):
        # Create a boolean, if needed.
        item = self.conf.get(confname)
        if item is None:
            item = bouwer.config.ConfigBool(confname)
            self.conf.active_tree.add(item)

        self.execute_config(item, function, lib, is_required)

    def execute_config(self, conf, function, lib, is_required = False):
        # Generate C file, if not yet done already.
        cfile = bouwer.util.tempfile(self.__class__.__name__ + '.' + conf.name + '.c')

        if not os.path.isfile(cfile):
            fp = open(cfile, 'w')
            fp.write('int ' + function + '();\nint main(void) { return ' + function + '(); }')
            fp.close()

        # Use the given library
        CCompiler.Instance().generate_library_override([lib])

        # Schedule Action to compile it
        CCompiler.Instance().c_program(TargetPath(cfile + '.o'),
                                      [SourcePath(cfile)],
                                       confitem=conf, function=function, library=lib,
                                       pretty_name='CHECK', pretty_target=function + ' in ' + lib,
                                       required=is_required, quiet=True)


    def action_event(self, action, event):
        """
        Called when an Action has finished
        """

        item = action.tags['confitem']

        # Update the configuration item
        if event.type == ActionEvent.FINISH and event.result != 0:
            if action.tags['required']:
                self.log.error('C function ' + action.tags['function'] +
                               ' does not exist in library ' + action.tags['library'])
                sys.exit(1)
            else:
                item.update(False)
        else:
            item.update(True)

        action.tags['pretty_target'] += ' ... ' + str(item.value())
