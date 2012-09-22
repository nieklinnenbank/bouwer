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

import sys
import os
import os.path
import inspect
import importlib

##
# Represents a loadable Bouwer plugin
#
class Plugin:

    ##
    # Constructor
    #
    def __init__(self, conf):
        self.conf  = conf
        self.build = None

    ##
    # Initialization routine of the plugin
    #
    def initialize(self, conf):
        pass

    ##
    # Check to see if this module has all external dependencies
    #
    def inspect(self):
        return True

    ##
    # Retrieve an Config item from the active tree.
    #
    # @param name Name of the Config item.
    # @return Config instance
    #
    def get_item(self, name):
        return self.conf.active_tree.subitems.get(name)

    ##
    # Generate an action
    #
    def action(self, target, command, sources):
        self.build.generate_action(target, command, sources)

    ##
    # Implements the self.OtherBuilder() mechanism
    #
    def __getattr__(self, name):
    
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in self.__dict__['build'].executes:
            return self.__dict__['build'].executes[name]
        else:
            raise AttributeError(name)

##
# Load all plugins in the given directory
#
class PluginLoader:

    def __init__(self, conf):

        self.conf    = conf
        self.plugins = {}

        # TODO: ugly long code!
        core_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        plug_path = core_path + os.sep + 'plugins'

        self._load_path(plug_path)
        self._load_path(conf.args.plugin_dir)

    ##
    # Load all plugins in the given directory
    #
    def _load_path(self, path):

        # The path must exist, otherwise don't attempt
        if not os.path.exists(path):
            return

        # Append source directory to the python path, if exists.
        if os.path.exists(path + os.sep + "__init__.py"):
            sys.path.insert(1, os.path.dirname(path))

        # Attempt to load all plugins in the given path
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:

                # Skip non python files
                if not filename.endswith(".py") or not filename[0].isupper():
                    continue

                # Begin loading the plugin
                if self.conf.args.verbose:
                    print('Loading ' + path + os.sep + filename)

                # Setup variables
                name, ext = os.path.splitext(filename)
                globs  = {}
                locs   = {}
                class_ = None

                # Construct load string
                loadstr = os.path.basename(path) + '.' + name

                # Import the builder as a module
                module = importlib.import_module(loadstr)

                # Find the plugin class, if any
                try:
                    class_ = getattr(module, name)
                except AttributeError:
                    pass

                # Initialize the plugin, if available
                if class_ is not None and Plugin in class_.__bases__:
                    instance = class_(self.conf)
                    instance.initialize(self.conf)

                    # Add plugin to the list
                    self.plugins[name] = instance
