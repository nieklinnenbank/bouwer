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
Bouwer configuration layer

Configuration allows the user to influence the execution
of the build automation system. A user can create and modify
a (set of) configuration(s) using any available configuration frontend.
For example, the :class:`.LineConfig` plugin allows the user to change
configuration items via the command line.
"""

import os
import sys
import logging
import inspect
import shlex
import json
from StringIO import StringIO
import bouwer.util

class Config(object):
    """
    Represents a single generic configuration item
    """

    def __init__(self, name, value, **keywords):
        """
        Constructor
        """
        self.name     = name
        self._value   = value
        self._keywords = keywords
        self.update(value)

    def get_key(self, key, default = None):
        """ Wrapper for the :obj:`dict.get` function """
        return self._keywords.get(key, default)

    def keys(self):
        """ Retrieve a list of keyword keys """
        return self._keywords.keys()

    def __getitem__(self, key):
        """
        Implements the conf_item['keyword'] mechanism.
        """
        try:
            return self._keywords[key]
        except KeyError:

            # TODO: there should be a clean way to ask for the item, which is directly
            #  "above" us in the override path
            # TODO: hack! we always take the base_conf as active dir...

            conf = Configuration.Instance()
            saved_dir = conf.active_dir
            conf.active_dir = conf.base_conf
            def_item = conf.trees['DEFAULT'].get(self.name)
            conf.active_dir = saved_dir

            if def_item is not None and def_item is not self:
                return def_item[key]
            else:
                raise KeyError('no such key: ' + str(key))

    def satisfied(self, tree = None):
        """
        See if we are satisfied with all our dependencies in `tree`

        If no `tree` is specified, the currently active tree will be searched
        """
        if tree is None:
            tree = Configuration.Instance().active_tree

        # See if our dependencies are met.
        for dep in self.get_key('depends', []):
            if tree.get(dep) is not None and not tree.get(dep).satisfied(tree):
                return False
            
        # If we are in a list, then we must be selected to satisfy.
        if self.get_key('in_list', False):
            lst = tree.get(self.get_key('in_list'))
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
        if 'depends' not in self._keywords:
            self._keywords['depends'] = []

        if item_name not in self._keywords['depends']:
            self._keywords['depends'].append(item_name)

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

    # TODO: refix this
    #def update(self, value):
    #    """
    #    Update the selected item in this list
    #    """
    #
    #    if value not in self.get_key('options'):
    #        raise Exception("item " + str(value) + " not in list " + self.name)
    #    else:
    #        super(ConfigList, self).update(value)

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
        for child_name in item.get_key('childs', []):
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
        if tree is None:
            tree = Configuration.Instance().active_tree

        return tree.name == self.name and super(ConfigTree, self).value(self)

    def __getattr__(self, name):
        """
        Implements the `conf.ITEM` mechanism
        """
        if name == self.name:
            return self
        elif name in self.__dict__:
            return self.__dict__[name]
        
        conf = Configuration.Instance()
        path = conf.active_dir # TODO: but what about this one ...

        if name in self.__dict__['subitems']:
            cfiles = self.__dict__['subitems'][name] 
           
            # See if there is a specific override
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
        elif name in conf.trees['DEFAULT'].subitems:
            return conf.trees['DEFAULT'].get(name)
        else:
            raise AttributeError('no such attribute: ' + str(name))

class BouwConfigParser:
    """
    Parser for Bouwconfig files
    """

    CONFIG_MODE  = 1
    CHOICE_MODE  = 2
    KEYWORD_MODE = 3
    HELP_MODE    = 4
    TREE_MODE    = 5

    def __init__(self, conf):
        """
        Constructor
        """
        # TODO: make these private
        self.conf       = conf
        self.log        = logging.getLogger(__name__)
        self.helpindent = None
        self.name       = None
        self.item       = None
        self.mode       = self.CONFIG_MODE
        self.syntax = { 'config'     : self._parse_config,
                        'choice'     : self._parse_choice,
                        'tree'       : self._parse_tree,
                        'configtree' : self._parse_configtree,
                        'keywords'   : self._parse_keywords,
                        'help'       : self._parse_help,
                        'default'    : self._parse_default,
                        'string'     : self._parse_string,
                        'tristate'   : self._parse_tristate,
                        'bool'       : self._parse_bool,
                        'override'   : self._parse_config, # TMP!!!
                        'endchoice'  : self._parse_endchoice,
                        'depends'    : self._parse_depends }

    def parse(self, filename):
        """
        Parse a Bouwconfig file
        """
        self.log.debug('reading `' + filename + '\'')

        self.name = None
        self.item = None

        for line in open(filename).readlines():
            if self.mode == self.KEYWORD_MODE:
                if line.find('=') == -1:
                    self.mode = self.CONFIG_MODE
                else:
                    parsed = line.partition('=')
                    key    = parsed[0].strip()
                    value  = parsed[2].strip()
                    self.item._keywords[key] = value
                    continue

            if self.mode == self.HELP_MODE:
                if self.helpindent is None:
                    self.helpindent = self._get_indent(line)

                if line.find(self.helpindent) == -1:
                    self.mode = self.HELP_MODE
                    self.helpindex = None
                else:
                    helpstr = line[ len(self.helpindent) : ]
                    continue
            
            self.parsed = shlex.split(line, True)
            if len(self.parsed) == 0:
                continue
            else:
                self.syntax[self.parsed[0]](line)

    def _get_indent(self, line):
        index = 0
        for char in line:
            if char in (' ', '\t'):
                index += 1
            else:
                break
        return line[:index]

    def _parse_depends(self, line):

        if 'depends' not in self.item._keywords:
            self.item._keywords['depends'] = []
        
        self.item._keywords['depends'].append(self.parsed[2])

    def _parse_keywords(self, line):
        self.mode = self.KEYWORD_MODE

    def _parse_config(self, line):
        self.name = self.parsed[1]
        self.tree = 'DEFAULT'
        self.mode = self.CONFIG_MODE

    def _parse_choice(self, line):
        self.name = self.parsed[1]
        self.tree = 'DEFAULT'
        self.mode = self.CHOICE_MODE
        # TODO: add it to the correct tree please
        # TODO: Add dependency to us for all list options
        #for opt in keywords['options']:
        #    dest_tree.get(opt).add_dependency(name)
        #    dest_tree.get(opt)._keywords['in_list'] = name
        #            
        # item = ConfigList(name)
        # self.conf.put(name)

    def _parse_endchoice(self, line):
        pass

    def _parse_tree(self, line):
        self.tree = self.parsed[1]

    def _parse_configtree(self, line):
        self.name = self.parsed[1]
        self.tree = 'DEFAULT'
        self.item = ConfigTree(self.name)
        self.conf.put(self.item, self.tree)

    def _parse_default(self, line):
        self.item._value = self.parsed[1]

    def _parse_string(self, line):
        self.item = ConfigString(self.name, '')
        self.conf.put(self.item, self.tree)

    def _parse_tristate(self, line):
        pass

    def _parse_override(self, line):
        pass

    def _parse_bool(self, line):
        if self.mode == self.CHOICE_MODE:
            self.item = ConfigList(self.name, '')
        else:
            self.item = ConfigBool(self.name)
        self.conf.put(self.item, self.tree)

    def _parse_help(self, line):
        self.mode = self.HELP_MODE

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
        self.parser = BouwConfigParser(self)

        # Find the path to the Bouwer predefined configuration files
        curr_file = inspect.getfile(inspect.currentframe())
        curr_dir  = os.path.dirname(os.path.abspath(curr_file))
        base_path = os.path.dirname(os.path.abspath(curr_dir + '..' + os.sep + '..' + os.sep))
        self.base_conf = base_path + os.sep + 'config'

        # The active tree and directory are used for
        # evaluation in the Config class, if needed.
        self.active_tree = None
        self.active_dir  = self.base_conf

        # Attempt to load saved config, otherwise reset to predefined.
        if not self.load():
            self.reset()

        # Validate tree
        # self._validate()

        # Dump configuration for debugging
        self.dump()

    def get(self, item_name):
        """
        Retrieve item named `item_name` from the active tree
        """
        return self.active_tree.get(item_name)

    def put(self, item, tree_name = 'DEFAULT'): 
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
                if tree_name is 'DEFAULT' or 'tree' in item._keywords:
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
        self.put(ConfigTree('DEFAULT'))
        self.active_tree = self.trees['DEFAULT']

        # Parse all pre-defined configurations from Bouwer
        self._scan_dir(self.base_conf)

        # Parse all user defined configurations
        self._scan_dir('.') #os.getcwd())

    def dump(self):
        """
        Dump the current configuration to the debug log
        """
        for tree_name, tree in self.trees.items():
            self._dump_item(tree, tree)

    def _validate(self):
        """
        Validate & enforce dependencies in all trees.
        """
        for tree_name, tree in self.trees.items():
            for item_name, paths in tree.subitems.items():
                for path_name, item in paths.items():
                    for dep in item.get_key('depends', []):

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
                
        for key in item._keywords:
            self.log.debug('\t' + key + ' => ' + str(item._keywords[key]))
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
        

