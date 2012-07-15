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
import inspect

class Environment(dict):

    ##
    # Class constructor
    #
    # @param name Name of the environment to initialize
    # @param global_config Reference to the configuration file
    #
    def __init__(self, name, global_config):

        global_config.set(name, 'id', name)

        self.name   = name
        self.config = global_config[name]
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
                if filename.endswith(".py"):
                    self._load_builder(path + '/' + filename)

    ##
    # Load the given builder.
    #
    # @param path Destination path of the builder
    #
    def _load_builder(self, path):

        globs = {}
        locs  = {}

        # Evaluate the module
        with open(path, "r") as f:
            exec(f.read(), globs, locs)
            f.close()

        # For each function, add it to ourselves
        for loc in locs:
            setattr(self.__class__, loc, locs[loc])

    ##
    # Implements the env[key] mechanism
    #
    # @param key Key name to read
    # @return Configuration item with the given key name
    #
    def __getitem__(self, key):
        return self.config[key]
