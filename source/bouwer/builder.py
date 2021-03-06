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
import shutil
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

        # TODO: also do a os.stat() in here and in TargetPath(), to avoid doing multiple os.stat()....
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
        root = self.conf.get('BUILDROOT').value()
        if root and not root.endswith('/'):
            root = root + '/'

        location = os.path.relpath( self.conf.active_dir ) #os.path.dirname(caller))

        # If only the default tree is active, don't prefix with tree name.
        if len(self.conf.trees) == 1:
            self.absolute = os.path.normpath(root + location + os.sep + path)
        else:
            self.absolute = os.path.normpath(root + self.conf.active_tree.name + \
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
        self.log = manager.log
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
            path = relative + os.sep + src

            src_list = glob.glob(path)
            if not src_list:
                src_list.append(path)

            # TODO: hmm. a lot of convertions here. needed?
            for src_file in src_list:
                out.append(SourcePath(os.path.dirname(src) + os.sep + os.path.basename(src_file)))

        return out

    def _invoke(self, *arguments, **keywords):
        """
        Call the correct execute function of the builder
        """

        self.log.debug("executing: " + str(self.builder.__class__.__name__) +
                       str(arguments) + ' ' +
                       ' (depends: ' + str(self.builder.config_input()) + ' ' +
                       ' provides: ' + str(self.builder.config_output()) +
                                       str(self.builder.config_action_output()) + ')')

        # if called with (target:str, source:str), convert to (target:str, [source:str]) automatically
        if arguments:
            if isinstance(arguments[0], bouwer.config.Config):

                # TODO: bug! how do we know the arguments list is a *FILES* list?
                if hasattr(self.builder, 'execute_config'):
                    return self.builder.execute_config(arguments[0],
                                                       self._source_path_list(arguments[1]),
                                                      *arguments[2:],
                                                      **keywords)

                if hasattr(self.builder, 'execute_config_params'): # TODO: <--- same as execute_any?
                    return self.builder.execute_config_params(*arguments, **keywords)

            elif type(arguments[0]) is str:
                if len(arguments) == 1 and hasattr(self.builder, 'execute_source'):
                    return self.builder.execute_source(SourcePath(arguments[0]), *arguments[1:], **keywords)

                elif hasattr(self.builder, 'execute_target'):
                    return self.builder.execute_target(TargetPath(arguments[0]),
                                                       self._source_path_list(arguments[1]),
                                                      *arguments[2:],
                                                      **keywords)

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

        # Instances found in Bouwfiles, pending execution.
        self.instances = []

        # Instance that is currently executing, if any.
        self.active_instance = None

        # Builders which can provide a particular config item.
        self.outputs   = {}
        self.log = logging.getLogger(__name__)

    # TODO: also take into account, the config items passed to execute()!
    # they should be marked as a configuration input for the builder!!!

    def insert(self, instance):
        """ Introduce a new builder instance """

        # Add to outputs list
        for output_item in instance.builder.config_output() + instance.builder.config_action_output():
            if output_item not in self.outputs:
                self.outputs[output_item] = []
            self.outputs[output_item].append(instance)

        self.instances.append(instance)

    def _try_execute(self, instance):
        """
        Try to execute the given builder instance
        BuilderInstance can only be executed if its Config inputs are satisfied.
        """
        if instance.run:
            return False

        # See if all our input configuration items are done
        for input_item in instance.builder.config_input():

            # Is the config item being produced in this round already?
            # Do not schedule right now then, because otherwise the dependency
            # is not met. 
            if input_item in self.conf_this_round:
                return False

            # See if any other builder needs to output for us first.
            if input_item in self.outputs:
                for output_instance in self.outputs[input_item]:
                    self._try_execute(output_instance)                  # TODO: recursion is limited!!! big projects have a LOT of instances .....
                return False

            # None means the configuration must be final
            if input_item is None:
                if len(self.outputs) > 0 or len(self.conf_this_round) > 0:
                    return False

        # If we got here, we may execute! Remove us from output list.
        for output_item in instance.builder.config_output():
            self.outputs[output_item].remove(instance)

            if len(self.outputs[output_item]) == 0:
                del self.outputs[output_item]

        # If the output needs to run an Action, it must prevent its dependencies to execute this round.
        for output_item in instance.builder.config_action_output():
            self.conf_this_round.append(output_item)
            self.outputs[output_item].remove(instance)
            
            if len(self.outputs[output_item]) == 0:
                del self.outputs[output_item]

        self.active_instance = instance
        instance.call()
        self.instances.remove(instance) # TODO: performance bottleneck?
        return True

    def execute(self):
        """
        Run all builders
        """
        while len(self.instances) > 0:
            inst  = self.instances[:]
            again = True
            self.conf_this_round = []

            while again:
                again = False
                for instance in inst:
                    if self._try_execute(instance):
                        again = True

            if self.manager.conf.args.clean:
                self.manager.actions.run(True)
                shutil.rmtree(bouwer.util.BOUWTEMP, True)
            else:
                self.manager.actions.run()

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
               hasattr(plugin, 'execute_config_params') or \
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
        self.parser    = BuilderParser(self)

    def execute(self, target, tree):
        """ 
        Generate actions associated with the given target.

        >>> manager.execute('build', conftree)
        """

        self.conf.active_tree = tree
        self.conf.get('TREE').update(self.conf.active_tree.name)
        if not tree.value():
            return

        self.log.debug("executing build target: `" + tree.name + ':' + target + "'")
        self.actions = bouwer.action.ActionManager()

        # Let the mesh execute its builders, and run its actions
        mesh = self.parser.parse('.', target)

        if mesh.instances:
            mesh.execute()
        else:
            self.log.error('no such target: ' + str(target))
            sys.exit(1)

    def action(self, target, sources, command, **tags):
        """ 
        Callback from builders to generate an Action

        :param str target: Target name of the new action
        :param list sources: List of dependencies
        :param str command: Command to execute
        :param event_handler: Action event handler is called on events.
        """

        # TODO: inefficient!
        src_list = []
        for src in sources:
            if type(src) is SourcePath or type(src) is TargetPath:
                src_list.append(src.absolute)
            else:
                src_list.append(src)

        # TODO: measure what is the best place to put this: inside the worker,
        # or here at the master?
        dirname = os.path.dirname(target.absolute)
        
        if len(dirname) > 0 and not os.path.exists(dirname):
            os.makedirs(dirname)

        self.actions.submit(target.absolute, src_list, command, tags,
                            self.parser.mesh.active_instance.builder)

