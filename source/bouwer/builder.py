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
import sys
import copy
import inspect
import importlib
import logging

##
# Responsible for access to the Builder layer.
#
class BuilderManager:

    ##
    # Class constructor
    #
    # @param conf Configuration instance
    # @param plugins Reference to available plugins
    #
    def __init__(self, conf, plugins):
        self.conf     = conf
        self.args     = conf.args
        self.log      = logging.getLogger(__name__)
        self.executes = {}

        # Detects all plugins with an execute() builder function
        for plugin_name, plugin in plugins.plugins.items():
            try:
                getattr(plugin, 'execute')
                self.executes[plugin_name] = plugin.execute
                plugin.build = self
            except AttributeError:
                pass

    ##
    # Generate Actions associated with the given target.
    #
    # @param target
    # @param tree Config tree instance.
    # @param actions
    #
    def execute_target(self, target, tree, actions):
        self.log.debug("executing `" + tree.name + ':' + target + "'")
        self.conf.active_tree = tree
        self.actions = actions
        self._scan_dir(os.getcwd(), target, tree, actions)

    ##
    # Scan a directory for Bouwfiles
    #
    # @param dirname Path to directory to scan
    # @param target
    # @param tree
    # @param actions
    #
    def _scan_dir(self, dirname, target, tree, actions):

        found = False

        # Look for all Bouwfiles.
        for filename in os.listdir(dirname):
            if filename.endswith('Bouwfile'):
                self._parse(dirname + os.sep + filename, target, tree, actions)
                found = True

        # Only scan subdirectories if at least one Bouwfile found.
        if found:
            for filename in os.listdir(dirname):
                if os.path.isdir(dirname + os.sep + filename):
                    self._scan_dir(dirname + os.sep + filename, target, tree, actions)

    ##
    # Parse a Bouwfile
    #
    # @param filename Path to the Bouwfile to parse.
    # @param target
    # @param tree
    # @param actions
    #
    def _parse(self, filename, target, tree, actions):

        self.log.debug("parsing `" + filename + "'")
    
        # Config file must be readable
        try:
            os.stat(filename)
        except OSError as e:
            self.log.critical("could not read Bouwfile `" + filename + "': " + str(e))
            sys.exit(1)

        globs = copy.copy(self.executes)

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), globs)

        # Execute the target routine, if defined in this Bouwfile.
        if target in globs:
            globs[target](tree)

    ##
    # Callback from builders to generate an Action
    #
    def generate_action(self, target, sources, command):
        self.actions.submit(target, sources, command)
