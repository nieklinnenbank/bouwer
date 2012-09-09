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
    # @param name Per-tree unique name of the configuration item.
    # @param value Initial value for the item.
    # @param type Type of the configuration item
    # @param dest_tree Configuration tree of the item
    # @param keywords Optional list of keywords
    #
    def __init__(self, name, value, type, dest_tree, **keywords):
        self.name        = name
        self.type        = type
        self.tree        = dest_tree
        self.keywords    = keywords
        self.subitems    = {}
        self.bouwconfigs = {}
        self.update(value)

    ##
    # See if all our dependencies are met in the given tree.
    # @param tree Reference to a tree Config object.
    # @return True if dependencies met, False otherwise.
    #
    def satisfied(self, tree):

        # See if our dependencies are met.
        for dep in self.keywords.get('depends', []):

            # Is the dependency an item?
            if dep in tree.subitems:
                if not tree.subitems[dep].satisfied(tree):
                    return False
                    
            # It's a tree
            elif dep is not tree.name or not tree.value:
                return False

        # Only booleans are interesting.        
        if self.type == bool:
            return self.value
        else:
            return True

    ##
    # Retrieve our values, also taking dependencies into account.
    # @param tree Reference tree to evaluate against
    # @return Current value of the item, respecting dependencies.
    #
    def evaluate(self, tree):
        if self.type is bool:
            return self.value and self.satisfied(tree)
        else:
            return self.value

    ##
    # Assign a new value to the item.
    # @param value New value for the item
    #
    def update(self, value):

        # Are we updating a list item?
        if self.type is list:

            # Given value must contain item from the default list
            if value not in self.keywords.get('default'):
                raise Exception("item " + str(value) + " not in list " + self.name)

            # Update selected option in the list
            self.value = value

            # Make sure only the selected item is true, for boolean lists
            if self.tree.subitems[value].type == bool:
                for opt_name in self.keywords.get('default'):
                    self.tree.subitems[opt_name].value = (opt_name == value)

        else:
            # TODO: Objects inside a list may not be updated directly
            self.value = value

    ##
    # Add an extra dependency.
    # @param item_name The given item name is the new dependency for us
    #
    def add_dependency(self, item_name):
        if 'depends' not in self.keywords:
            self.keywords['depends'] = []

        if item_name not in self.keywords['depends']:
            self.keywords['depends'].append(item_name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

##
# Parser class for Bouwconfig files.
#
class ConfigParser:

    ##
    # Constructor
    # @param conf Reference to Configuration object
    #
    def __init__(self, conf):
        self.conf = conf

    ##
    # Prepare arguments for creating a Config() object.
    #
    def _prepare(self, name, **keywords):

        item_value = keywords.get('default', True)
        item_type  = type(item_value)
        dest_tree  = self.conf.trees[keywords.get('tree', 'DEFAULT')]

        # Let all childs depend on the item
        for child in keywords.get('childs', []):
            dest_tree.subitems[child].add_dependency(name)

        return item_type, item_value, dest_tree

    ##
    # Parse a Config() line.
    # @param name
    # @param keywords
    # @return Name of the item just added
    #
    def parse_config(self, name, **keywords):

        item_type, item_value, dest_tree = self._prepare(name, **keywords)

        # In case of a list, make the options depend on us
        if item_type is list:

            # Default selected option is the first.
            item_value = keywords['default'][0]

            # Add dependency to us for all list options
            for opt in keywords['default']:
                dest_tree.subitems[opt].add_dependency(name)
                dest_tree.subitems[opt].keywords['in_list'] = name

                # It's also possible to configure the default selected item.
                if 'selected' in dest_tree.subitems[opt].keywords:
                    item_value = opt

        # Create the config item
        self.conf.insert_item(name, item_value, item_type, dest_tree, **keywords)
        return name

    ##
    # Parse a ConfigTree() line.
    # @param name
    # @param keywords
    # @return Name of the tree just added
    #
    def parse_config_tree(self, name, **keywords):

        item_type, item_value, dest_tree = self._prepare(name, **keywords)

        assert(item_type is bool)
        assert(type(item_value) is bool)

        self.conf.insert_tree(name, item_value, **keywords)
        return name
        

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
        self.trees = {}

        # Attempt to load saved config, otherwise reset to predefined.
        if not self.load():
            self.reset()

        # Dump configuration for debugging
        if self.args.verbose:
            self.dump()

    ##
    # Introduce a new configuration item
    #
    def insert_item(self, name, value, type, dest_tree, **keywords):

        # Does the item already exist?        
        if name in dest_tree.subitems:
            raise Exception('item ' + name + ' already exists in tree ' + dest_tree.name)

        # Create item
        item = Config(name, value, type, dest_tree, **keywords)
        
        # Insert item to the tree
        dest_tree.subitems[name] = item
        
        # Lookup Bouwconfig path
        path = os.path.abspath(inspect.getfile(inspect.currentframe().f_back.f_back))
        if not path in dest_tree.bouwconfigs:
            dest_tree.bouwconfigs[path] = []

        # Insert item to the bouwconfig mapping
        dest_tree.bouwconfigs[path].append(item)

    ##
    # Introduce a new configuration tree
    #
    def insert_tree(self, name, value, **keywords):
        self.trees[name] = Config(name, value, bool, None, **keywords)

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

        # Insert the default tree.
        self.insert_tree('DEFAULT', True)

        # Find the path to the Bouwer predefined configuration files
        curr_file = inspect.getfile(inspect.currentframe())
        curr_dir  = os.path.dirname(os.path.abspath(curr_file))
        base_path = os.path.dirname(os.path.abspath(curr_dir + '..' + os.sep + '..' + os.sep))
        conf_path = base_path + os.sep + 'config'

        # Parse all pre-defined configurations from Bouwer
        self._scan_dir(conf_path)

        # Parse all user defined configurations
        self._scan_dir(os.getcwd())

        # Synchronize configuration trees
        self._synchronize()

    ##
    # Dump the current configuration to standard output
    #
    def dump(self):
        for tree_name, tree in self.trees.items():
            self._dump_item(tree, tree)

    ##
    # Make sure all configuration trees contain at least the default items
    #
    def _synchronize(self):    

        def_tree = self.trees.get('DEFAULT')

        # Make sure user-defined trees inherit all items from
        # the default tree, unless they are overwriten.
        for tree_name, tree in self.trees.items():
            if tree_name is def_tree.name:
                continue

            # Inherit every default item per bouwconfig
            for path in def_tree.bouwconfigs:
                for item in def_tree.bouwconfigs[path]:

                    # Create path in custom tree, if needed.
                    if path not in tree.bouwconfigs:
                        tree.bouwconfigs[path] = []

                    # Is the item overwritten?
                    if item.name in tree.subitems:
                        # Inherit keywords from the default item, if not overwritten
                        custom_item = tree.subitems[item.name]

                        for key in item.keywords:
                            if key not in custom_item.keywords:
                                custom_item.keywords[key] = item.keywords[key]

                        # TODO: be careful when overwriting lists, or list items!
                        pass

                    # Inherit the item
                    else:
                        tree.bouwconfigs[path].append(item)
                        tree.subitems[item.name] = item

        # Validate & enforce dependencies in all trees.
        for tree_name, tree in self.trees.items():
            for item_name, item in tree.subitems.items():
                for dep in item.keywords.get('depends', []):

                    # Is it an unknown dependency?
                    if dep not in tree.subitems and \
                       dep not in self.trees:
                        raise Exception('Unknown dependency item ' + dep + ' in ' + item_name)

                    # TODO: add circular dependency check

    ##
    # Dump a single configuration item to stdout
    # @param item Config object to dump
    # @param tree Tree of the item
    # @param parent Text describing the parent item
    #
    def _dump_item(self, item, tree, parent = ''):
        print(parent + str(item) + ':' + str(item.type) + ' = ' + str(item.evaluate(tree)) + '(' + str(item.value) + ')')
                
        for key in item.keywords:
            print('\t' + key + ' => ' + str(item.keywords[key]))
        print()

        for child_item_name, child_item in item.subitems.items():
            self._dump_item(child_item, tree, parent + item.name + '.')

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

        # Initialize parser of Bouwconfig files.
        parser =  ConfigParser(self)
        globs  = { 'Config':     parser.parse_config,
                   'ConfigTree': parser.parse_config_tree }

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), globs)
