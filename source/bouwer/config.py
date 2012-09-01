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
import inspect
import pickle

##
# Represents a single configuration item
#
class Config:

    ##
    # Constructor
    #
    def __init__(self, name, **keywords):
        self.name     = name
        self.keywords = keywords
        self.subitems = {}
        self.value    = keywords.get('default', True)
        self.type     = type(self.value)
        self.depends  = keywords.get('depends', [])

        # Let all of our childs depend on us    
        for child in keywords.get('childs', []):
            child.depends.append(self)

        # In case of a list, make the options also a rev dependency
        if self.type is list:

            # Default selected option is the first.
            self.value = self.keywords['default'][0]

            # It's also possible to configure the default selected item.
            for item in self.keywords['default']:
                if 'selected' in item.keywords:
                    self.value = item
                    break

            # Set dependency to us for all options            
            for item in self.keywords['default']:
                item.depends.append(self)

                # Make sure only the default boolean option is True
                if item.type == bool:
                   item.value = (item == self.value)

        # Store the location of the Bouwfile where we are declared
        self.bouwfile = os.path.abspath(inspect.getfile(inspect.currentframe().f_back))
                                
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

##
# Wrapper for accessing Configuration
#
class ConfigWrapper:

    ##
    # Constructor
    #
    def __init__(self, conf):
        self.conf = conf

    ##
    # Add an item to the Configuration
    #
    def put_item(self, name, **keywords):
        return self.conf.insert_item(Config(name, **keywords))

    ##
    # Add a new configuration tree
    #
    def put_tree(self, name, **keywords):
        return self.conf.insert_tree(Config(name, **keywords))
        

##
# Represents the current configuration
#
class Configuration:

    ##
    # Constructor
    # @param cli CommandLine object for reading arguments
    #
    def __init__(self, cli):
        self.cli   = cli
        self.args  = cli.args
        self.trees = { 'DEFAULT': Config('DEFAULT') }

        # Attempt to load saved config, otherwise reset to predefined.
        if not self.load():
            self.reset()

        # Dump configuration for debugging
        if self.args.verbose:
            self.dump()

    ##
    # Introduce a new configuration item
    # @param obj Config object to insert
    # @param tree Name of the tree to insert object or NONE for default tree.
    #
    def insert_item(self, obj, tree = None):
        self.trees[obj.keywords.get('tree', 'DEFAULT')].subitems[obj.name] = obj
        return obj

    ##
    # Introduce a new configuration tree
    # @param obj Config object for the tree
    #
    def insert_tree(self, obj):
        self.trees[obj.name] = obj
        return obj

    ##
    # Load a saved configuration from the given file
    # @param filename Path to the saved configuration file
    #
    def load(self, filename = '.bouwconf'):
        return False

    ##
    # Save current configuration to the given file
    # @param filename Path to the configuration output file
    #
    def save(self, filename = '.bouwconf'):
        pass

    ##
    # Reset configuration to the initial predefined state
    #
    def reset(self):

        # Find the path to the Bouwer predefined configuration files
        curr_file = inspect.getfile(inspect.currentframe())
        curr_dir  = os.path.dirname(os.path.abspath(curr_file))
        base_path = os.path.dirname(os.path.abspath(curr_dir + '..' + os.sep + '..' + os.sep))
        conf_path = base_path + os.sep + 'config'

        # Parse all pre-defined configurations from Bouwer
        self._scan_dir(conf_path)

        # Parse all user defined configurations
        self._scan_dir(os.getcwd())

        # TODO: synchronize configuration trees!!!

    ##
    # Dump the current configuration to standard output
    #
    def dump(self):
        for tree_name, tree in self.trees.items():
            self._dump_item(tree)

    ##
    # Dump a single configuration item to stdout
    # @param item Config object to dump
    # @param parent Text describing the parent item
    #
    def _dump_item(self, item, parent = ''):
        print(parent + str(item) + ' ' + str(item.keywords))
        for child_item_name, child_item in item.subitems.items():
            self._dump_item(child_item, parent + item.name + '.')

    ##
    # Scan a directory for configuration definition files.
    # @param dirname Path to directory to scan
    #
    def _scan_dir(self, dirname):

        found = False

        # Look for all Bouwconfig's.
        for filename in os.listdir(dirname):
            if filename.endswith('Bouwconfig'):
                self._parse(dirname + os.sep + filename)
                found = True

        # Only scan subdirectories if at least one Bouwconfig found.
        if found:        
            for filename in os.listdir(dirname):
                if os.path.isdir(dirname + os.sep + filename):
                    self._scan_dir(dirname + os.sep + filename)
        
    ##
    # Parse configuration definition file
    # @param filename Path to the configuration file
    ##
    def _parse(self, filename):

        # Output message
        if self.args.verbose:
            print(sys.argv[0] + ': reading `' + filename + '\'')

        # Config file must be readable
        try:
            os.stat(filename)
        except OSError as e:
            print(sys.argv[0] + ": could not read config file '" + filename + "': " + str(e))
            sys.exit(1)

        # Initialize wrapper for adding item to ourselves
        wrapper = ConfigWrapper(self)
        globs = { 'Config':     wrapper.put_item,
                  'ConfigTree': wrapper.put_tree }

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), globs)
