#
# Copyright (C) 2012 Niek Linnenbank <nieklinnenbank@gmail.com>
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
Builder layer module
"""

import os
import os.path
import sys
import copy
import logging
import inspect
import glob

import bouwer.config
from bouwer.util import *

class BuilderInvoker:
    """
    Responsible for calling the correct execute function of a builder
    """

    def __init__(self, manager, builder):
        """ Constructor """
        self.manager = manager
        self.builder = builder

    def _source_path_list(self, input_list):

        if type(input_list) is str:
            input_list = [input_list]

        out = []
        for src in input_list:

            bouwfile = self.manager.active_bouwfile
            caller   = os.path.abspath(bouwfile)
            relative = os.path.relpath(os.path.dirname(caller))

            # TODO: hmm. a lot of convertions here. needed?
            for src_file in glob.glob(relative + os.sep + src):
                out.append(SourcePath(os.path.dirname(src) + os.sep + os.path.basename(src_file)))

        return out

    def invoke(self, *arguments, **keywords):
        """
        Call the correct execute function of the builder
        """

        # if called with (target:str, source:str), convert to (target:str, [source:str]) automatically
        if isinstance(arguments[0], bouwer.config.Config):
            return self.builder.execute_config(arguments[0],
                                               self._source_path_list(arguments[1]))

        elif type(arguments[0]) is str:
            if len(arguments) == 1 and hasattr(self.builder, 'execute_source'):
                return self.builder.execute_source(SourcePath(arguments[0]))

            elif hasattr(self.builder, 'execute_target'):
                return self.builder.execute_target(TargetPath(arguments[0]),
                                                   self._source_path_list(arguments[1]))

        elif type(arguments[0]) is TargetPath:
            return self.builder.execute_target(*arguments)

        elif type(arguments[0]) is SourcePath:
            return self.builder.execute_source(*arguments)

        return self.builder.execute_any(*arguments, **keywords)

class BuilderManager(Singleton):
    """ 
    Manages access to the builder layer
    """

    def __init__(self, conf = None, plugins = None):
        """ 
        Class constructor

        :Input:
            - ``conf`` (:class:`.Configuration`)   -- Current configuration
            - ``plugins`` (:class:`.PluginLoader`) -- Access to loaded plugins 

        """
        self.conf     = conf
        self.args     = conf.args
        self.log      = logging.getLogger(__name__)
        self.invokers = {}

        # Detects all plugins with an execute() builder function
        for plugin_name, plugin in plugins.plugins.items():
            if hasattr(plugin, 'execute_target') or \
               hasattr(plugin, 'execute_config') or \
               hasattr(plugin, 'execute_source') or \
               hasattr(plugin, 'execute_any'):
                
                self.invokers[plugin_name] = BuilderInvoker(self, plugin).invoke
                plugin.build = self

    def execute_target(self, target, tree, actions):
        """ 
        Generate actions associated with the given target.

        Input:
            - ``target`` (:py:obj:`str`)  -- Name of the target to execute
            - ``tree`` (:class:`.Config`) -- Current configuration tree

        Output:
            - ``actions`` (:class:`.ActionTree`) -- Destination action tree

        Example:
            >>> manager.execute_target('build', conftree, actiontree)

        """
        self.log.debug("executing `" + tree.name + ':' + target + "'")
        self.conf.active_tree = tree
        self.actions = actions
        self._scan_dir(os.getcwd(), target, tree, actions)

    def _scan_dir(self, dirname, target, tree, actions):
        """ 
        Scan a directory for Bouwfiles

        Input:
            - ``dirname`` (:py:obj:`str`) -- Path to directory to scan
            - ``target`` (:py:obj:`str`)  -- Target name
            - ``tree`` (:class:`.Config`) -- Current configuration tree

        Output:
            - ``actions`` (:class:`.ActionTree`) -- Destination action tree

        """
        found = False

        # Look for all Bouwfiles.
        for filename in os.listdir(dirname):
            if filename.endswith('Bouwfile'):
                self._parse(dirname + os.sep + filename, target, tree, actions)
                found = True

        # Only scan subdirectories if at least one Bouwfile found.
        if found:
            for filename in os.listdir(dirname):
                if os.path.isdir(dirname + os.sep + filename):
                    self._scan_dir(dirname + os.sep + filename,
                                   target, tree, actions)

    def _parse(self, filename, target, tree, actions):
        """ 
        Parse a Bouwfile
        """
        self.log.debug("parsing `" + filename + "'")
    
        # Config file must be readable
        try:
            os.stat(filename)
        except OSError as e:
            self.log.critical("could not read Bouwfile `" +
                               filename + "': " + str(e))
            sys.exit(1)

        # Keep track of the Bouwfile being parsed
        self.active_bouwfile = filename

        # Set globals
        globs = copy.copy(self.invokers)

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), globs)

        # Execute the target routine, if defined in this Bouwfile.
        if target in globs:
            globs[target](tree)

    def translate_source(self, source, conf):
        """
        Translate Bouwfile-relative source to project-wide source path
        """
        caller   = os.path.abspath(self.active_bouwfile)
        relative = os.path.relpath(os.path.dirname(caller))
        return os.path.normpath(relative + os.sep + source)

    def translate_target(self, target, conf):
        """
        Translate Bouwfile-relative target to project-wide target path
        """
        # TODO: if only DEFAULT is active, don't add the tree name in the path
        # TODO: support the BUILDROOT, BUILDPATH configuration items

        # TODO: remove conf, or make it always conf.active_tree

        caller   = os.path.abspath(self.active_bouwfile)
        #inspect.getfile(inspect.currentframe().f_back.f_back))
        relative = os.path.relpath(os.path.dirname(caller))

        if len(self.conf.trees) == 1:
            return os.path.normpath(relative + os.sep + target)
        else:
            return os.path.normpath(conf.name + os.sep + relative + os.sep + target)

    def generate_action(self, target, sources, command):
        """ 
        Callback from builders to generate an Action

        :param str target: Target name of the new action
        :param list sources: List of dependencies
        :param str command: Command to execute

        """

        # TODO: inefficient!
        src_list = []
        for src in sources:
            src_list.append(src.absolute)

        # TODO: measure what is the best place to put this: inside the worker,
        # or here at the master?
        dirname = os.path.dirname(target.absolute)
        
        if len(dirname) > 0 and not os.path.exists(dirname):
            os.makedirs(dirname)

        self.actions.submit(target.absolute, src_list, command)

