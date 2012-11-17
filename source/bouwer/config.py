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

"""
Bouwer configuration layer implementation
"""

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
            tree = Configuration.Instance().active_tree

        # See if our dependencies are met.
        for dep in self.keywords.get('depends', []):
            if tree.get(dep) is not None and not tree.get(dep).satisfied(tree):
                return False
            
        # If we are in a list, then we must be selected to satisfy.
        if self.keywords.get('in_list', False):
            lst = tree.get(self.keywords.get('in_list'))
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

    def inherit_keywords(self, other):
        """ temporary routine to copy keywords from other item """
        # TODO: this should be replaced by keyword indirection/evaluation
        for key in other.keywords:
            if key not in self.keywords:
                self.keywords[key] = other.keywords[key]

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
        raise Exception('reimplement this')
        # TODO: can we improve this?
        """
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
        """

    def __str__(self):
        """ String representation """
        return str(self.value())

    def __repr__(self):
        """ Interactive representation """
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
            tree = Configuration.Instance().active_tree
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
    """
    Integer configuration item
    """
    pass

class ConfigFloat:
    """
    Floating point number configuration item
    """
    pass

class ConfigTri:
    """
    Tristate configuration item
    """
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

    def add(self, item):
        """
        Introduce a new :class:`.Config` item to the tree
        """

        # Every item in the tree contains a dict with
        # paths for which it is active or overriden
        # TODO: make sure this only contains the 'projectwide path' and not absolute OS path
        if item.name not in self.subitems:
            self.subitems[item.name] = {}
            path = Configuration.Instance().base_conf
        else:
            path = Configuration.Instance().active_dir
       
        # Add to the subitems dict
        self.subitems[item.name][path] = item
 
        # Let all childs depend on the item
        for child_name in item.keywords.get('childs', []):
            # TODO: validate that the child is there!

            for path, child in self.subitems[child_name].items():
                child.add_dependency(item.name)

    def get(self, item_name):
        """
        Retrieve item in this tree with the given `item_name`
        """
        try:
            return getattr(self, item_name)
        except AttributeError:
            return None

    def satisfied(self, tree = None):
        """
        See if we are satisfied with all our dependencies in `tree`

        If no `tree` is specified, the currently active tree will be searched
        """
        if tree is None:
            tree = Configuration.Instance().active_tree

        return tree is self

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
        elif name in self.__dict__:
            return self.__dict__[name]
        
        conf = Configuration.Instance()
        path = conf.active_dir

        if name in self.__dict__['subitems']:
            cfiles = self.__dict__['subitems'][name] 
            
            # Make a loop which 'climbs' the basename()/basedir() of the path, until a match is found,
            # if nothing found, return the base_conf as a last attempt, otherwise the item doesnt exist
            while path is not '':
                if path in cfiles:
                    return cfiles[path]
                else:
                    path = os.path.dirname(path)

            # If not overriden, return the default
            if conf.base_conf in cfiles:
                return cfiles[conf.base_conf]
        elif name in conf.trees:
            return conf.trees[name]
        else:
            raise AttributeError('no such attribute: ' + str(name))

class ConfigParser:
    """
    Parser for Bouwconfig files
    """

    def __init__(self, conf):
        """
        Constructor
        """
        # TODO: make these private
        self.conf  = conf
        self.log   = logging.getLogger(__name__)
        self.globs = { 'ConfigBool'   : self._parse_bool,
                       'ConfigString' : self._parse_string,
                       'ConfigList'   : self._parse_list,
                       'ConfigTree'   : self._parse_tree }

    def _get_value(self, **keywords):
        """ Retrieve default value """
        if 'default' in keywords:
            return ( (keywords['default']), )
        else:
            return ()

    def parse(self, filename):
        """
        Parse a Bouwconfig file
        """
        self.log.debug('reading `' + filename + '\'')

        # Config file must be readable
        try:
            os.stat(filename)
        except OSError as e:
            self.log.critical("could not read config file '" + filename + "': " + str(e))
            sys.exit(1)

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), self.globs)

    def _parse_bool(self, name, *opts, **keywords):
        """
        Handles a `ConfigBool` line
        """
        self.conf.insert(ConfigBool(name,
                                   *self._get_value(**keywords),
                                  **keywords), *opts)
        return name

    def _parse_string(self, name, *opts, **keywords):
        """
        Handles a `ConfigString` line
        """
        self.conf.insert(ConfigString(name,
                                     *self._get_value(**keywords),
                                    **keywords), *opts)
        return name

    def _parse_list(self, name, *opts, **keywords):
        """
        Handles a `ConfigList` line
        """
        if len(opts) > 1:
            dest_tree = Configuration.Instance().trees[opts]
        else:
            dest_tree = Configuration.Instance().trees['DEFAULT']

        # Add dependency to us for all list options
        for opt in keywords['options']:
            dest_tree.get(opt).add_dependency(name)
            dest_tree.get(opt).keywords['in_list'] = name

        self.conf.insert(ConfigList(name,
                                   *self._get_value(**keywords),
                                  **keywords), dest_tree.name)
        return name

    def _parse_tree(self, name, *opts, **keywords):
        """
        Handles a `ConfigTree` line
        """
        self.conf.insert(ConfigTree(name,
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
        self.cli    = cli
        self.log    = logging.getLogger(__name__)
        self.args   = cli.args
        self.trees  = {}
        self.parser = ConfigParser(self)

        # Find the path to the Bouwer predefined configuration files
        curr_file = inspect.getfile(inspect.currentframe())
        curr_dir  = os.path.dirname(os.path.abspath(curr_file))
        base_path = os.path.dirname(os.path.abspath(curr_dir + '..' + os.sep + '..' + os.sep))
        self.base_conf = base_path + os.sep + 'config'

        # The active tree and directory are used for
        # evaluation in the Config class, if needed.
        self.active_tree = None
        self.active_dir  = None

        # Attempt to load saved config, otherwise reset to predefined.
        if not self.load():
            self.reset()

        # Dump configuration for debugging
        self.dump()

    def get(self, item_name):
        """
        Retrieve item named `item_name` from the active tree
        """
        return self.active_tree.get(item_name)

    def insert(self, item, tree_name = 'DEFAULT'): 
        """
        Introduce a new :class:`.Config` object `item`
        """
        if isinstance(item, ConfigTree):
            self.trees[item.name] = item
        else:
            self.trees[tree_name].add(item)

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
        self.insert(ConfigTree('DEFAULT'))

        # Parse all pre-defined configurations from Bouwer
        self._scan_dir(self.base_conf)

        # Parse all user defined configurations
        self._scan_dir('.') #os.getcwd())

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

        # TODO: replace this with a constant, e.g. Configuration.DEFAULT or ConfigTree.DEFAULT or self.DEFAULT
        def_tree = self.trees.get('DEFAULT')

        # Make sure user-defined trees inherit all items from
        # the default tree, unless they are overwriten.
        for tree_name, tree in self.trees.items():
            if tree_name is def_tree.name:

                # TODO: temporary let overrides inherit from the original
                # TODO: this should be replaced by the keywords indirection stuff
                for item_name, paths in def_tree.subitems.items():
                    for path, item in paths.items():
                        if path is not self.base_conf and self.base_conf in paths:
                            item.inherit_keywords(paths[self.base_conf])
                continue

            # Inherit every default item
            for item_name, paths in def_tree.subitems.items():
                for path_name, item in paths.items():

                    # Is the item overwritten?
                    if item.name in tree.subitems:

                        # Inherit keywords from the default item, if not overwritten
                        custom_item_confs = tree.subitems[item.name]

                        # For every instance, inherit the keywords
                        for custom_item_cfile, custom_item in custom_item_confs.items():
                            custom_item.inherit_keywords(item)

                        # TODO: make sure to remove orphan childs, when a list is overwritten!
                        pass

                    # Inherit the item
                    else:
                        tree.subitems[item.name] = { path_name: item }

        # Validate & enforce dependencies in all trees.
        for tree_name, tree in self.trees.items():
            for item_name, paths in tree.subitems.items():
                for path_name, item in paths.items():
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
        # TODO: perhaps put the dump method in ConfigTree itself?
        if isinstance(item, ConfigTree):
            for child_item_name, paths in item.subitems.items():
                for path, child_item in paths.items():
                    self._dump_item(child_item, tree, parent + item.name + '.')

    def _scan_dir(self, dirname):
        """
        Scans a directory for Bouwconfig files
        """
        found = False

        # Look for all Bouwconfig's.
        for filename in os.listdir(dirname):
            # TODO: replace 'Bouwconfig' literal with a constant, e.g. BOUWCONF or something or CONFFILE
            if filename.endswith('Bouwconfig'):
                self.active_dir = dirname
                self.parser.parse(dirname + os.sep + filename)
                found = True

        # Only scan subdirectories if at least one Bouwconfig found.
        if found:        
            for filename in os.listdir(dirname):
                if os.path.isdir(dirname + os.sep + filename):
                    self._scan_dir(dirname + os.sep + filename)
        

