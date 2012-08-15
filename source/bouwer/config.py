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

##
# Represents a single configuration item
#
class Config:

    # Reference to the Configuration object
    global config

    ##
    # Constructor
    #
    def __init__(self, name, **keywords):
        self.name     = name
        self.keywords = keywords

        # See if the 'tree' keyword exists.
        if 'tree' in keywords:

            # Try to inherit from the existing item, if any
            try:
                item = config.get_item(name)

                for key in item.keywords:
                    if key not in keywords:
                        keywords[key] = item.keywords[key]
            except Exception as e:
                print(e)
                pass

            # Add item to the specific config tree
            config.add_item(name, self, keywords['tree'])

        # Add item to Configuration
        else:
            config.add_item(name, self)
##
# Represents a configuration tree
#
class ConfigTree:

    # Reference to the Configuration object
    global config

    ##
    # Constructor
    #
    def __init__(self, name, **keywords):
        self.name     = name
        self.keywords = keywords
        self.items    = {}
        config.add_tree(name, self)

##
# Represents the current configuration
#
class Configuration:

    # Constructor
    def __init__(self, args):
        self.args  = args
        self.items = {}
        self.trees = {}

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
        self.trees[name] = obj

    # Add a configuration item
    def add_item(self, name, obj, tree = None):
        if tree is None:
            self.items[name] = obj
        else:
            self.trees[tree].items[name] = obj

    # Find an configuration item, e.g. 'VERSION'
    def get_item(self, name):
        return self.items[name]

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
            os.stat(filename)
        except OSError as e:
            print(sys.argv[0] + ": could not read config file '" + filename + "': " + str(e))
            sys.exit(1)

        # Parse the given file
        config = self
        exec(compile(open(filename).read(), filename, 'exec'))

    ##
    # Dump the current configuration to standard output
    #
    def dump(self):

        # Dump all configuration trees
        for tree_name in self.trees:

            tree = self.trees[tree_name]
            print(str(tree.name))

            for key in tree.keywords:
                print('\t' + str(key) + ' = ' + str(tree.keywords[key]))

            for item_name in tree.items:
                item = tree.items[item_name]

                print('')
                print('\t' + str(item.name))

                for key in item.keywords:
                    print('\t\t' + str(key) + ' = ' + str(item.keywords[key]))
