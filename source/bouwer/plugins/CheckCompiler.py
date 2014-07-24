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

from bouwer.plugin import *
from bouwer.builder import *
import bouwer.util

class CheckCompiler(Plugin):
    """
    Check if the given compiler exists
    """

    def config_action_output(self):
        return [ 'CC' ]

    def execute_config(self, item):
        # Save input C compiler
        self.cc = self.conf.get(item.value())

        # Generate C file, if not yet done already.
        cfile = bouwer.util.tempfile(self.__class__.__name__ + '.' + self.cc.name + '.c')

        if not os.path.isfile(cfile):
            fp = open(cfile, 'w')
            fp.write('int main(void) { return 0; }')
            fp.close()

        # TODO: use the CCompiler module?
        # Schedule Action to compile it
        self.build.action(TargetPath(cfile + '.o'),
                         [SourcePath(cfile)],
                          self.cc['cc'] + ' ' + cfile + '.o ' +
                          self.cc['ccflags'] + ' ' + cfile,
                          pretty_name='CHK',
                          pretty_target=self.cc.name)

    def action_event(self, action, event):
        """
        Called when an Action has finished
        """
        if event.type == ActionEvent.FINISH:
            if event.result != 0:
                # The C compiler cannot generate C objects.
                # TODO: Try the next C compiler automatically, if any.
                self.log.error('C compiler not installed or unable to execute: ' + str(self.cc.name))
                sys.exit(1)

            action.tags['pretty_target'] += ' ... True'
