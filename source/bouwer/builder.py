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
import glob
import bouwer.config
import bouwer.util

class Path(object):
    """
    Abstract representation of a file path
    """

    def __init__(self, path):
        """ Constructor """
        self.relative = path
        self.absolute = path
        self.build    = bouwer.builder.BuilderManager.Instance()
        self.conf     = bouwer.config.Configuration.Instance()

    def append(self, text):
        """ Append text to the path """
        self.relative += text
        self.absolute += text

    def __str__(self):
        """ Convert path to string """
        return str(self.absolute)

class SourcePath(Path):
    """
    Implements a `path` to a source file
    """

    def __init__(self, path):
        """
        Constructor
        """
        super().__init__(path)
        caller   = os.path.abspath(self.build.active_bouwfile)
        location = os.path.relpath(os.path.dirname(caller))
        self.absolute = os.path.normpath(location + os.sep + path)

class TargetPath(Path):
    """
    Path to a target output file based on a source `path`
    """

    def __init__(self, path):
        """
        Constructor
        """
        super().__init__(path)
        # TODO: support the BUILDROOT, BUILDPATH configuration items
        # TODO: use Configuration.Instance().active_dir instead
        caller   = os.path.abspath(self.build.active_bouwfile)
        location = os.path.relpath(os.path.dirname(caller))

        # If only the default tree is active, don't prefix with tree name.
        if len(self.conf.trees) == 1:
            self.absolute = os.path.normpath(location + os.sep + path)
        else:
            self.absolute = os.path.normpath(self.conf.active_tree.name + \
                                             os.sep + location + os.sep + path)

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

class BuilderManager(bouwer.util.Singleton):
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
        # Update the active directory for Config evaluation
        self.conf.active_dir = os.path.dirname(os.path.abspath(filename))
        self.log.debug("conf.active_dir = " + self.conf.active_dir)
        self.active_bouwfile = filename

        # Set globals
        globs = copy.copy(self.invokers)

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), globs)

        # Execute the target routine, if defined in this Bouwfile.
        if target in globs:
            globs[target](tree)

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


