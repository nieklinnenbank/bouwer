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
Plugin extensions support
"""

import sys
import os
import os.path
import inspect
import logging
import importlib
from bouwer.util import Singleton
from bouwer.config import Configuration
from bouwer.builder import BuilderManager

class Plugin:
    """
    Bouwer plugin class
    """

    def __init__(self):
        """
        Constructor
        """
        self.conf  = Configuration.Instance()
        self.build = BuilderManager.Instance()

    def config_input(self):
        """ Configuration items as input """
        return []

    def config_output(self):
        """ Configuration items as output """
        return []

    # TODO: why not add the prototypes here?
    # and then call that via BuildInstance?
    # The default prototypes could just invoke each other..
    # def execute_config()
    # def finished(self, action):
    def completed(self, action):
        pass

    def initialize(self):
        """ Initialize the plugin """
        pass

class PluginManager(Singleton):
    """
    Manages loading plugins
    """

    def __init__(self):
        """ Constructor """

        self.conf    = Configuration.Instance()
        self.log     = logging.getLogger(__name__)
        self.plugins = {}

        # TODO: ugly long code!
        core_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        plug_path = core_path + os.sep + 'plugins'

        self._load_path(plug_path)
        self._load_path(self.conf.args.plugin_dir)

    ##
    # Load all plugins in the given directory
    #
    def _load_path(self, path):

        # The path must exist, otherwise don't attempt
        if not os.path.exists(path):
            return

        # Append source directory to the python path, if exists.
        if os.path.exists(path + os.sep + "__init__.py"):
            sys.path.insert(1, os.path.dirname(path))
            sys.path.insert(1, path)

        # Attempt to load all plugins in the given path
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:

                # Skip non python files
                if not filename.endswith(".py") or not filename[0].isupper():
                    continue

                # Begin loading the plugin
                self.log.debug('loading ' + path + os.sep + filename)

                # Setup variables
                name, ext = os.path.splitext(filename)
                class_ = None

                # Construct load string
                loadstr = os.path.basename(path) + '.' + name

                # Import the builder as a module
                module = importlib.import_module(loadstr)

                # Find the plugin class, if any
                try:
                    class_ = getattr(module, name)
                except AttributeError:
                    pass

                # Initialize the plugin, if available
                if class_ is not None and Plugin in class_.__bases__:
                    instance = class_()
                    instance.initialize()

                    # Add plugin to the list
                    self.plugins[name] = instance

    # TODO: replace this with: def invoke(func, ...), e.g. invoke('output', foo, bar, zzz):

    ##
    # Retrieves the active output plugin
    #
    def output_plugin(self):

        # If the output_plugin parameter is set, use that.
        try:
            return self.conf.args.output_plugin
        except AttributeError:
            pass
    
        # Look for the first plugin with an output() function.
        for plugin_name, plugin in self.plugins.items():
            try:
                getattr(plugin, 'output')
                return plugin
            except AttributeError:
                pass

        # No output plugin available.
        return None
