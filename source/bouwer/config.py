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
import bouwer.util

class Config(object):
    """
    Represents a single generic configuration item
    """

    def __init__(self, name, value, **keywords):
        """
        Constructor
        """
        self.name        = name
        self._value      = value
        self.keywords    = keywords
        self.update(value)

    def satisfied(self, tree = None):
        """
        See if we are satisfied with all our dependencies in `tree`

        If no `tree` is specified, the currently active tree will be searched
        """
        if tree is None:
            tree = Configuration.instance().active_tree

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

        # TODO: hack
        if type(self._value) is bool:
            return self._value
        else:
            return True

    def value(self, tree = None):
        """
        Retrieve the current value of the configuration item
        """
        return self._value

    def update(self, value):
        """
        Assign a new `value` to the configuration item
        """
        self._value = value

    def add_dependency(self, item_name):
        """
        Introduce a new dependency on `item_name`
        """
        if 'depends' not in self.keywords:
            self.keywords['depends'] = []

        if item_name not in self.keywords['depends']:
            self.keywords['depends'].append(item_name)

    def serialize(self):
        """
        Return JSON serializable representation of the item
        """
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

    def __str__(self):
        return str(self.value())

    def __repr__(self):
        return self.name

class ConfigBool(Config):
    """
    Boolean configuration item

    This type of configuration item can only be `True` or `False`.
    """

    def __init__(self, name, value = True, **keywords):
        """
        Constructor
        """
        super(ConfigBool, self).__init__(name, value, **keywords)

    def value(self, tree = None):
        """
        Retrieve our value, also taking dependencies into account.
        """
        if tree is None:
            tree = Configuration.instance().active_tree
        return self._value and self.satisfied(tree)

    def update(self, value):
        """
        Update the `value` of this boolean item
        """
        if type(value) is not bool:
            raise Exception('value must be either True or False')
        else:
            super(ConfigBool, self).update(value)

class ConfigString(Config):
    """
    String configuration item

    This type of configuration item contains any string value,
    which must be of the basic type `str`. Empty strings are allowed.
    """

    def update(self, value):
        """
        Update the `value` of this string item
        """
        if type(value) is not str:
            raise Exception('value must be a string')
        else:
            super(ConfigString, self).update(value)

class ConfigList(Config):
    """
    List configuration item
    """

    def __init__(self, name, value = None, **keywords):
        """
        Constructor
        """
        if value is None:
            value = keywords['options'][0]
        super(ConfigList, self).__init__(name, value, **keywords)

    def update(self, value):
        """
        Update the selected item in this list
        """
        if value not in self.keywords.get('options'):
            raise Exception("item " + str(value) + " not in list " + self.name)
        else:
            super(ConfigList, self).update(value)

class ConfigInt:
    pass

class ConfigFloat:
    pass

class ConfigTri:
    pass

class ConfigTree(ConfigBool):
    """
    Tree configuration items can contain other configuration items
    """

    def __init__(self, name, value = True, **keywords):
        """
        Constructor
        """
        super(ConfigTree, self).__init__(name, value, **keywords)
        self.subitems    = {}
        self.bouwconfigs = {}

    def value(self, tree = None):
        """
        Retrieve value of the tree. Either `True` or `False`.
        """
        return super(ConfigTree, self).value(self)

    def __getattr__(self, name):
        """
        Implements the `conf.ITEM` mechanism
        """
        if name == self.name:
            return self
        try:
            return self.__dict__[name]
        except KeyError:
            return self.subitems[name]

class ConfigParser:
    """
    Parser for Bouwconfig files
    """

    def __init__(self, conf):
        """ Constructor """
        self.conf = conf

    def _get_value(self, **keywords):
        if 'default' in keywords:
            return ( (keywords['default']), )
        else:
            return ()

    def parse_bool(self, name, *opts, **keywords):
        """
        Handles a `ConfigBool` line
        """
        self.conf.insert_item(ConfigBool(name,
                                        *self._get_value(**keywords),
                                       **keywords), *opts)
        return name

    def parse_string(self, name, *opts, **keywords):
        """
        Handles a `ConfigString` line
        """
        self.conf.insert_item(ConfigString(name,
                                          *self._get_value(**keywords),
                                         **keywords), *opts)
        return name

    def parse_list(self, name, *opts, **keywords):
        """
        Handles a `ConfigList` line
        """

        # Find destination tree
        if len(opts) > 1:
            dest_tree = Configuration.instance().trees[opts]
        else:
            dest_tree = Configuration.instance().trees['DEFAULT']

        # Add dependency to us for all list options
        for opt in keywords['options']:
            dest_tree.subitems[opt].add_dependency(name)
            dest_tree.subitems[opt].keywords['in_list'] = name

        self.conf.insert_item(ConfigList(name,
                                        *self._get_value(**keywords),
                                       **keywords), dest_tree.name)
        return name

    def parse_tree(self, name, *opts, **keywords):
        """
        Handles a `ConfigTree` line
        """
        self.conf.insert_tree(ConfigTree(name,
                                        *self._get_value(**keywords),
                                       **keywords))
        return name

class Configuration(bouwer.util.Singleton):
    """
    Represents the current configuration
    """

    def __init__(self, cli = None):
        """
        Constructor
        """
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

    def insert_item(self, item, tree_name = 'DEFAULT'): 
        """
        Introduce a new configuration item
        """
        # Find destination tree
        dest_tree = self.trees[tree_name]

        # Does the item already exist?        
        if item.name in dest_tree.subitems:
            raise Exception('item ' + item.name + ' already exists in tree ' + dest_tree.name)

        # Insert item to the tree
        dest_tree.subitems[item.name] = item
 
        # Let all childs depend on the item
        for child in item.keywords.get('childs', []):
            dest_tree.subitems[child].add_dependency(item.name)

        # Lookup Bouwconfig path
        path = os.path.abspath(inspect.getfile(inspect.currentframe().f_back.f_back))
        if not path in dest_tree.bouwconfigs:
            dest_tree.bouwconfigs[path] = []

        # Insert item to the bouwconfig mapping
        dest_tree.bouwconfigs[path].append(item)

    def insert_tree(self, tree):
        """
        Introduce a new configuration tree
        """
        if not isinstance(tree, ConfigTree):
            raise TypeError('input tree must be of type ConfigTree')

        self.trees[tree.name] = tree

    def load(self, filename = '.bouwconf'):
        """
        Load a saved configuration from the given `filename`
        """
        return False

    def save(self, filename = '.bouwconf'):
        """
        Save the current configuration to `filename`
        """
        fp = open(filename, 'w')

        # Save only default tree items and overwrites        
        for tree_name, tree in self.trees.items():
            self._save_item(tree, fp)
        
            for item_name, item in tree.subitems.items():
                if tree_name is 'DEFAULT' or 'tree' in item.keywords:
                    self._save_item(item, fp)

        fp.close()

    def _save_item(self, item, fp):
        """
        Save a single configuration item
        """
        json.dump(item.serialize(), fp, sort_keys=True, indent=4)
        fp.write(os.linesep)

    def reset(self):
        """
        Reset configuration to the initial predefined state using Bouwconfigs
        """
        # Insert the default tree.
        self.insert_tree(ConfigTree('DEFAULT'))

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

    def write_header(self, filename, tree_name = None):
        """
        Output the given configuration tree as a C header file

        The settings will be encoded as #define's
        """
        # TODO: put this in the ConfigHeader() builder instead...
        self.log.debug("writing configuration to header: " + str(filename))

    def dump(self):
        """
        Dump the current configuration to the debug log
        """
        for tree_name, tree in self.trees.items():
            self._dump_item(tree, tree)

    def _synchronize(self):
        """
        Make sure all configuration trees contain at least the default items
        """
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

    def _dump_item(self, item, tree, parent = ''):
        """
        Dump a single configuration item
        """

        self.log.debug(parent + item.name + ':' + str(item.__class__) + ' = ' + str(item.value(tree)))
                
        for key in item.keywords:
            self.log.debug('\t' + key + ' => ' + str(item.keywords[key]))
        self.log.debug('')

        # TODO: this dumping could be improved...
        if isinstance(item, ConfigTree):
            for child_item_name, child_item in item.subitems.items():
                self._dump_item(child_item, tree, parent + item.name + '.')

    def _scan_dir(self, dirname):
        """
        Scans a directory for Bouwconfig files
        """
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
        
    def _parse(self, filename):
        """
        Parse a Bouwconfig file
        """
        # TODO: perhaps move this to ConfigParser instead?

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
        globs  = { 'ConfigBool'   : parser.parse_bool,
                   'ConfigString' : parser.parse_string,
                   'ConfigList'   : parser.parse_list,
                   'ConfigTree'   : parser.parse_tree }

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), globs)

