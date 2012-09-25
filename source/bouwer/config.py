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
import logging
import inspect
import json
import bouwer.builder

##
# Represents a single configuration item
#
class Config:

    ##
    # Constructor
    #
    # @param name Per-tree unique name of the configuration item.
    # @param value Initial value for the item.
    # @param type Type of the configuration item
    # @param config Reference to the Configuration we belong in
    # @param keywords Optional list of keywords
    #
    def __init__(self, name, value, type, config, **keywords):
        self.name        = name
        self.type        = type
        self.keywords    = keywords
        self.config      = config
        self.subitems    = {}
        self.bouwconfigs = {}
        self.update(value)

    ##
    # See if all our dependencies are met in the given tree.
    #
    # @param tree Reference to a tree Config object.
    # @return True if dependencies met, False otherwise.
    #
    def satisfied(self, tree = None):

        if tree is None:
            tree = self.config.active_tree

        # See if our dependencies are met.
        for dep in self.keywords.get('depends', []):

            # Is the dependency an item?
            if dep in tree.subitems:
                if not tree.subitems[dep].satisfied(tree):
                    return False
                    
            # It's a tree
            elif dep is not tree.name or not tree.value:
                return False

        # If we are in a list, then we must be selected to satisfy.
        if self.keywords.get('in_list', False):
            lst = tree.subitems[self.keywords.get('in_list')]
            return lst.value(tree) == self.name

        # Only booleans are interesting.
        if self.type == bool:
            return self._value
        else:
            return True

    ##
    # Retrieve our values, also taking dependencies into account.
    #
    # @param tree Reference tree to evaluate against
    # @return Current value of the item, respecting dependencies.
    #
    def value(self, tree = None):

        if tree is None:
            tree = self.config.active_tree
    
        if self.type is bool:
            return self._value and self.satisfied(tree)
        else:
            return self._value

    ##
    # Assign a new value to the item.
    #
    # @param value New value for the item
    #
    def update(self, value):

        # Are we updating a list item?
        if self.type is list:

            # Sanity check. Given value must be in the list.
            if value not in self.keywords.get('default'):
                raise Exception("item " + str(value) + " not in list " + self.name)
        
        # Assign value        
        self._value = value

    ##
    # Add an extra dependency.
    #
    # @param item_name The given item name is the new dependency for us
    #
    def add_dependency(self, item_name):
        if 'depends' not in self.keywords:
            self.keywords['depends'] = []

        if item_name not in self.keywords['depends']:
            self.keywords['depends'].append(item_name)

    ##
    # Return a JSON serializable representation
    #
    def serialize(self):
    
        # TODO: can we improve this?
        bouwconf_map = {}

        for path in self.bouwconfigs:
            bouwconf_map[path] = []
        
            for item in self.bouwconfigs[path]:
                bouwconf_map[path].append(item.name)
    
        return dict(name = self.name,
                    type = str(self.type),
                    value = str(self._value),
                    keywords = self.keywords,
                    bouwconfigs = bouwconf_map)

    ##
    # Implements the conf.ITEM mechanism
    #
    def __getattr__(self, name):

        if name == self.name:
            return self

        try:
            return self.__dict__[name]
        except KeyError:
            return self.subitems[name]

    def __str__(self):
        return str(self.value()) #value) # TODO: this is wrong. we need to evaluate() against the *active* tree

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
        self.log   = logging.getLogger(__name__)
        self.args  = cli.args
        self.trees = {}
        
        # The active tree is used for evaluation in Config, if needed.
        self.active_tree = None

        # Attempt to load saved config, otherwise reset to predefined.
        if not self.load():
            self.reset()

        # Dump configuration for debugging
        self.dump()

    ##
    # Introduce a new configuration item
    #
    def insert_item(self, name, value, type, dest_tree, **keywords):

        # Does the item already exist?        
        if name in dest_tree.subitems:
            raise Exception('item ' + name + ' already exists in tree ' + dest_tree.name)

        # Create item
        item = Config(name, value, type, self, **keywords)
        
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
        self.trees[name] = Config(name, value, bool, self, **keywords)

    ##
    # Load a saved configuration from the given file
    # @param filename Path to the saved configuration file
    #
    def load(self, filename = '.bouwconf'):
        # TODO
        return False

    ##
    # Save current configuration to the given file
    # @param filename Path to the configuration output file
    #
    def save(self, filename = '.bouwconf'):
    
        fp = open(filename, 'w')

        # Save only default tree items and overwrites        
        for tree_name, tree in self.trees.items():
            self._save_item(tree, fp)
        
            for item_name, item in tree.subitems.items():
                if tree_name is 'DEFAULT' or 'tree' in item.keywords:
                    self._save_item(item, fp)

        fp.close()

    def _save_item(self, item, fp):
        json.dump(item.serialize(), fp, sort_keys=True, indent=4)
        fp.write(os.linesep)

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

                        # TODO: make sure to remove orphan childs, when a list is overwritten!
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
        
        self.log.debug(parent + item.name + ':' + str(item.type) + ' = ' + str(item.value(tree)))
                
        for key in item.keywords:
            self.log.debug('\t' + key + ' => ' + str(item.keywords[key]))
        self.log.debug('')

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
        self.log.debug('reading `' + filename + '\'')

        # Config file must be readable
        try:
            os.stat(filename)
        except OSError as e:
            self.log.critical("could not read config file '" + filename + "': " + str(e))
            sys.exit(1)

        # Initialize parser of Bouwconfig files.
        parser =  ConfigParser(self)
        globs  = { 'Config':     parser.parse_config,
                   'ConfigTree': parser.parse_config_tree }

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), globs)
