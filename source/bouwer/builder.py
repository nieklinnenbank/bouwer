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
import bouwer.action
import bouwer.util
import bouwer.plugin

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
        super(SourcePath, self).__init__(path)
        #caller   = os.path.abspath(self.build.active_bouwfile)
        location = os.path.relpath(self.conf.active_dir) #os.path.dirname(caller))
        self.absolute = os.path.normpath(location + os.sep + path)

class TargetPath(Path):
    """
    Path to a target output file based on a source `path`
    """

    def __init__(self, path):
        """
        Constructor
        """
        super(TargetPath, self).__init__(path)
        # TODO: support the BUILDROOT, BUILDPATH configuration items
        # TODO: use Configuration.Instance().active_dir instead
        #caller   = os.path.abspath(self.build.active_bouwfile)
        location = os.path.relpath( self.conf.active_dir ) #os.path.dirname(caller))

        # If only the default tree is active, don't prefix with tree name.
        if len(self.conf.trees) == 1:
            self.absolute = os.path.normpath(location + os.sep + path)
        else:
            self.absolute = os.path.normpath(self.conf.active_tree.name + \
                                             os.sep + location + os.sep + path)

class BuilderInstance:
    """
    Represents a builder line in a Bouwfile
    """

    def __init__(self, manager, builder, active_dir, *arguments, **keywords):
        """ Constructor """
        self.manager = manager
        self.builder = builder
        self.active_dir = active_dir
        self.arguments = arguments
        self.keywords = keywords
        self.run = False

    def call(self):
        """ Execute the builder """
        self.manager.conf.active_dir = self.active_dir
        self._invoke(*self.arguments, **self.keywords)
        self.run = True

    def _source_path_list(self, input_list):
        """ Convert input list to a `list` of :class:`.SourcePath` """

        if type(input_list) is str:
            input_list = [input_list]

        out = []
        for src in input_list:
            relative = self.manager.conf.active_dir

            # TODO: hmm. a lot of convertions here. needed?
            for src_file in glob.glob(relative + os.sep + src):
                out.append(SourcePath(os.path.dirname(src) + os.sep + os.path.basename(src_file)))

        return out

    def _invoke(self, *arguments, **keywords):
        """
        Call the correct execute function of the builder
        """

        # if called with (target:str, source:str), convert to (target:str, [source:str]) automatically
        if isinstance(arguments[0], bouwer.config.Config):

            # TODO: bug! how do we know the arguments list is a *FILES* list?
            if hasattr(self.builder, 'execute_config'):
                return self.builder.execute_config(arguments[0],
                                                   self._source_path_list(arguments[1]))
            else:
                return self.builder.execute_config_params(*arguments)

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

    def __str__(self):
        return "BuilderInstance: " + str(self.builder) + "," + str(self.arguments) + "," + str(self.keywords)

    def __repr__(self):
        return str(self)

class BuilderGenerator:
    """
    Helper class to insert a :class:`.BuilderInstance`
    """

    def __init__(self, manager, mesh, name, plugin):
        self.manager = manager
        self.mesh = mesh
        self.name = name
        self.plugin = plugin

    def insert(self, *arguments, **keywords):
        self.mesh.insert( BuilderInstance(self.manager, self.plugin, self.manager.conf.active_dir, *arguments, **keywords))

class BuilderMesh:
    """
    Holds all builder instances
    """

    def __init__(self, manager):
        """ Constructor """
        self.manager = manager
        self.conf = self.manager.conf

        self.instances = []
        self.outputs   = {}

        self.log = logging.getLogger(__name__)

    # TODO: also take into account, the config items passed to execute()!
    # they should be marked as a configuration input for the builder!!!

    def insert(self, instance):
        """ Introduce a new builder instance """
        self.manager.log.debug("inserting instance: " + str(instance))

        # Add to outputs list
        for output_item in instance.builder.config_output():
            if output_item not in self.outputs:
                self.outputs[output_item] = []
            self.outputs[output_item].append(instance)

        self.instances.append(instance)

    def _try_execute(self, instance):
        """
        Try to execute the given builder instance
        """
        if instance.run: return

        # See if all our input configuration items are done
        for input_item in instance.builder.config_input():
            if input_item in self.outputs:
                for output_instance in self.outputs[input_item]:
                    self._try_execute(output_instance)
                return

        # If we got here, we may execute!
        for output_item in instance.builder.config_output():
            self.outputs[output_item].remove(instance)

            if len(self.outputs[output_item]) == 0:
                del self.outputs[output_item]

        self.log.debug("executing instance: " + str(instance))
        instance.call()
        self.instances.remove(instance) # TODO: performance bottleneck?

    def execute(self):
        """
        Run all builders
        """
        while len(self.instances) > 0:
            inst = self.instances[:]

            for instance in inst:
                self._try_execute(instance)

            # Now execute all generated actions
            self.log.debug("executing all actions!")

class BuilderParser:
    """
    Parses Bouwfiles for executing builders
    """

    def __init__(self, manager):
        """
        Constructor
        """
        self.manager   = manager
        self.mesh = BuilderMesh(manager)
        self.builders = {}
        self.log = logging.getLogger(__name__)
 
        # Detects all plugins with an execute() builder function
        for plugin_name, plugin in bouwer.plugin.PluginManager.Instance().plugins.items():
            if hasattr(plugin, 'execute_target') or \
               hasattr(plugin, 'execute_config') or \
               hasattr(plugin, 'execute_source') or \
               hasattr(plugin, 'execute_any'):

                self.log.debug("builder: " + plugin_name)
                self.builders[plugin_name] = BuilderGenerator(self.manager, self.mesh, plugin_name, plugin).insert

    def parse(self, dirname, target):
        """ 
        Scan a directory for Bouwfiles
        """
        found = False

        # Look for all Bouwfiles.
        for filename in os.listdir(dirname):
            if filename.endswith('Bouwfile'):
                self._parse_bouwfile(dirname + os.sep + filename, target)
                found = True

        # Only scan subdirectories if at least one Bouwfile found.
        if found:
            for filename in os.listdir(dirname):
                if os.path.isdir(dirname + os.sep + filename):
                    self.parse(dirname + os.sep + filename, target)

        return self.mesh

    def _parse_bouwfile(self, filename, target):
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
        self.manager.conf.active_dir = os.path.dirname(filename)

        # Set globals
        globs = copy.copy(self.builders)

        # Parse the given file
        exec(compile(open(filename).read(), filename, 'exec'), globs)

        # Execute the target routine, if defined in this Bouwfile.
        if target in globs:
            globs[target](self.manager.conf.active_tree)

class BuilderManager(bouwer.util.Singleton):
    """ 
    Manages access to the builder layer
    """

    def __init__(self):
        """ 
        Constructor
        """
        self.conf      = bouwer.config.Configuration.Instance() 
        self.args      = self.conf.args
        self.log       = logging.getLogger(__name__)
        self.datastore = {}
        self.parser    = BuilderParser(self)

    def execute(self, target, tree):
        """ 
        Generate actions associated with the given target.

        >>> manager.execute('build', conftree)
        """
        self.log.debug("executing `" + tree.name + ':' + target + "'")
        self.conf.active_tree = tree

        self.actions = bouwer.action.ActionManager(self.conf.args)

        mesh = self.parser.parse('.', target)
        #mesh.inspect()
        mesh.execute()
        #self._scan_dir('.', target, tree, actions)

        # Dump generated actions?
        # TODO: please do this better... ugly :-(
        if self.conf.args.verbose:
            self.actions.dump()

        # Run or clean the actions?
        if self.conf.args.clean:
            self.actions.clean()
        else:
            self.actions.run()

    def put(self, key, value):
        """
        Publish a `key` and `value` pair for sharing with other builders

        The datastore mechanism in the :class:`.BuildManager` allows
        a builder plugin to share information with other builder plugins.
        For instance, the :class:`.UseLibrary` plugin requires information
        about the path of libraries from the :class:`.Library` builder.
        """
        self.datastore[key] = value

    def get(self, key):
        """
        Retrieve the value of `key` published by another builder
        """
        return self.datastore[key]

    def action(self, target, sources, command):
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

