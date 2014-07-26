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
from CCompiler import CCompiler

# TODO: make these classes inherit from a generic check class.

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

class CheckLibrary(Plugin):
    def execute_any(self, confname, library, is_required = False):
        # Create a boolean, if needed.
        item = self.conf.get(confname)
        if item is None:
            item = bouwer.config.ConfigBool(confname)
            self.conf.active_tree.add(item)

        self.execute_config(item, library, is_required)

    def execute_config(self, conf, library, is_required = False):
        # Generate C file, if not yet done already.
        cfile = bouwer.util.tempfile(self.__class__.__name__ + '.' + conf.name + '.c')
        tfile = TargetPath(cfile + '.o')

        if not os.path.isfile(cfile):
            fp = open(cfile, 'w')
            fp.write('int main(void) { return 0; }')
            fp.close()

        # Use the given library
        CCompiler.Instance().use_library([library], tfile)

        # Seperate object action, which does not have pretty output.
        CCompiler.Instance().c_object(SourcePath(cfile), item=conf, pretty_skip=True)

        # Schedule Action to compile it
        CCompiler.Instance().c_program(tfile, [],
                                       item=conf, confitem=conf, library=library,
                                       pretty_name='CHK', pretty_target='lib'+library,
                                       required=is_required, quiet=True)

    def action_event(self, action, event):
        """
        Called when an Action has finished
        """

        try:
            item = action.tags['confitem']
        except:
            return

        # Update the configuration item on finish.
        if event.type == ActionEvent.FINISH:
            if event.result != 0:

                # Make sure the target file is updated.
                open(action.target, 'w').close()

                if action.tags['required']:
                    self.log.error('library \'' + action.tags['library'] + '\''
                                   ' cannot be found')
                    sys.exit(1)
                else:
                    item.update(False)
            else:
                item.update(True)

            # Fancy output
            action.tags['pretty_target'] += ' ... ' + str(item.value())


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
        tfile = TargetPath(cfile + '.o')

        if not os.path.isfile(cfile):
            fp = open(cfile, 'w')
            fp.write('int ' + function + '();\nint main(void) { return ' + function + '(); }')
            fp.close()

        # Use the given library
        CCompiler.Instance().use_library([lib], tfile)

        # Seperate object action, which does not have pretty output.
        CCompiler.Instance().c_object(SourcePath(cfile), item=conf, pretty_skip=True)

        # Schedule Action to compile it
        CCompiler.Instance().c_program(tfile, [],
                                       item=conf, confitem=conf, function=function, library=lib,
                                       pretty_name='CHK', pretty_target=function,
                                       required=is_required, quiet=True)

    def action_event(self, action, event):
        """
        Called when an Action has finished
        """

        try:
            item = action.tags['confitem']
        except:
            return

        # Update the configuration item on finish.
        if event.type == ActionEvent.FINISH:
            if event.result != 0:

                # Make sure the target file is updated.
                open(action.target, 'w').close()

                if action.tags['required']:
                    self.log.error('C function ' + action.tags['function'] +
                                   ' does not exist in library ' + action.tags['library'])
                    sys.exit(1)
                else:
                    item.update(False)
            else:
                item.update(True)

            # Fancy output
            action.tags['pretty_target'] += ' ... ' + str(item.value())

class CheckHeader(Plugin):
    """
    See if a C header exists.
    """

    def config_input(self):
        return [ 'CC' ]

    def config_action_output(self):
        return [ 'CHECK' ]

    def execute_any(self, confname, header, is_required = False):
        # Create a boolean, if needed.
        item = self.conf.get(confname)
        if item is None:
            item = bouwer.config.ConfigBool(confname)
            self.conf.active_tree.add(item)

        self.execute_config(item, header, is_required)

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
                                      pretty_name='CHK', pretty_target=header,
                                      standalone=True, required=is_required, quiet=True)

    def action_event(self, action, event):
        """
        Called when an Action has finished
        """

        item = action.tags['confitem']

        # Update the configuration item
        if event.type == ActionEvent.FINISH:
            if event.result != 0:
                if action.tags['required']:
                    self.log.error('C Header ' + action.tags['filename'] + ' not installed')
                    sys.exit(1)
                else:
                    item.update(False)
            else:
                item.update(True)

            action.tags['pretty_target'] += ' ... ' + str(item.value())
