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
import sys
import configparser

# Reference to the active Configuration object
config = None

class Config:

    def __init__(self, name, **keywords):
        global config

        self.name     = name
        self.keywords = keywords

        # First inherit keywords of an existing item, if it exists
        # TODO

        # Then add the item to the active tree
        config.add_item(name, self)

class ConfigTree(Config):

    def __init__(self, name, **keywords):
        global config
        self.name = name
        self.keywords = keywords
        config.add_tree(name, self)

##
# Represents the current configuration
#
class Configuration:

    # Constructor
    def __init__(self, args):
        self.args = args
        pass

    # output config to a C header config.h file:
    #
    # enabled:
    #
    #    #define CONFIG_$NAME $VALUE
    # or:
    #
    #    /* CONFIG_$NAME */
    #
    def write_header(self, path):
        pass

    # Add a configuration tree
    def add_tree(self, name, obj):
        pass

    # Add a configuration item
    def add_item(self, name, obj):
        pass

    # Find an configuration item, e.g. 'VERSION'
    def get_item(self, name):
        pass

    # Find the first config item with the given key, e.g. 'cc'
    def get_item_by_key(self, key):
        pass

    ##
    # Parse configuration in the given file
    # @param filename Path to the configuration file
    # @return Reference to the generated configuration
    ##
    def parse(self, filename):

        global config

        # Output message
        if self.args.verbose:
            print(sys.argv[0] + ': reading `' + filename + '\'')

        # Config file must be readable
        try:
            os.stat(self.args.config)
        except OSError as e:
            print(sys.argv[0] + ": could not read config file '" + filename + "': " + str(e))
            sys.exit(1)

        # Parse the given file
        config = self
        exec(compile(open(filename).read(), filename, 'exec'))
