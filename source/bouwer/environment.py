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

##
# Represents a build configuration for executing Actions.
#
class Environment(dict):

    ##
    # Class constructor
    #
    # @param name Name of the environment to initialize
    # @param global_config Reference to the configuration file
    # @param action_tree Reference to the actions tree
    #
    def __init__(self, name, config, args, action_tree):
        self.name     = name
        self.config   = config
        self.config.set(name, 'id', name)
        self.args     = args
        self.bouwfile = None
        self.action   = action_tree
        self.buildroot_map = {} # translates the full project path to the
                                # build root path, e.g:
                                #   src/module/foo.o -> build/src/module/foo.o
        self._load_builders(self._get_load_dir() + '/builder')

    ##
    # Find the directory of the currently executing file.
    #
    # @return Path to the current directory of this file.
    #
    def _get_load_dir(self):
        cur_file = os.path.abspath(inspect.getfile(inspect.currentframe()))
        return os.path.dirname(cur_file)

    ##
    # Load all python modules in a directory as builders.
    #
    # @param path Destination directory containing builder modules.
    #
    def _load_builders(self, path):

        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".py") and filename != '__init__.py':
                    self._load_builder(path + '/' + filename)

    ##
    # Load the given builder.
    #
    # @param path Destination path of the builder
    #
    def _load_builder(self, path):

        name = os.path.basename(os.path.splitext(path)[0])

        # Import the builder as a module
        module = importlib.import_module('bouwer.builder.' + name)
        class_ = getattr(module, name)
        instance = class_(self)

        # Add the execute function to ourselves
        setattr(self.__class__, name, instance.execute)

    ##
    # Evaluate the given python module.
    #
    # @param path Path to the python module to execute
    # @param globs Dictionary with globals
    # @param locs Dictionary with locals
    #
    def _run_module(self, path, globs, locs):

        # Evaluate the module
        # TODO: if this goes wrong, it only shows <string> as source
        with open(path, "r") as f:
            exec(f.read(), globs, locs)
            f.close()

    ##
    # Implements the env[key] mechanism
    #
    # @param key Key name to read
    # @return Configuration item with the given key name
    #
    def __getitem__(self, key):
        return self.config[self.name][key]

    ##
    # Register all targets with the given name by recursing in all directories.
    #
    def register_targets(self, target):

        if self.args.verbose:
            print(sys.argv[0] + ": executing `" + target + "'")

        # Look for Action scripts in all subdirectories
        for dirname, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                if filename == self.args.script:

                    self.bouwfile = os.path.join(dirname, filename)

                    if self.args.verbose:
                        print(sys.argv[0] + ': parsing `' + self.bouwfile + '\'')

                    globs = {}
                    locs  = {}

                    # Parse the Bouwfile
                    self._run_module(self.bouwfile, globs, locs)

                    # Save current configuration
                    # TODO: this cannot be done with configparser object
                    # TODO: solution: make our own Config class instead
                    #saved_config = copy.deepcopy(self.config)
                    saved_config = copy.copy(self.config)

                    # execute the build target
                    if target in locs:
                        locs[target](self)

                    # Restore configuration
                    self.config = saved_config

    ##
    # Register an Action for execution.
    #
    def register_action(self, target, action, sources, pretty = None):

        # Honour the buildroot setting
        buildroot = self['buildroot'] + os.sep + self['id']

        # Full path to the target from the top-level Bouwfile
        full_target = os.path.dirname(self.bouwfile) + os.sep + target

        # Real path to the target, using a buildroot
        real_dir    = buildroot + os.sep + os.path.dirname(self.bouwfile[2:])
        real_target = real_dir + os.sep + target

        # Fill the buildmap
        self.buildroot_map[full_target] = real_target

        # Make sure the sources have absolute paths
        real_sources = []

        # Find absolute paths of the sources
        for src in sources:
            real_src = os.path.dirname(self.bouwfile) + os.sep + src

            # This source may have a real target in the buildroot
            if real_src in self.buildroot_map:
                real_sources.append(self.buildroot_map[real_src])
            else:
                real_sources.append(real_src)

        # For verbose execution, remove pretty output
        if self.args.verbose:
            pretty = None

        # Add new Action to the ActionTree
        self.action.add(real_target, action, real_sources, self, pretty)
