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
from bouwer.action import ActionEvent

class Plugin:
    """
    Bouwer plugin class
    """

    def __init__(self):
        """
        Constructor
        """
        self.conf   = Configuration.Instance()
        self.build  = BuilderManager.Instance()
        self.log    = logging.getLogger(__name__)

    def config_input(self):
        """ Configuration items as input """
        return []

    def config_output(self):
        """ Configuration items as output """
        return []

    def config_action_output(self):
        """ Configuration items as output that need to run an Action """
        return []

    # TODO: why not add the prototypes here?
    # and then call that via BuildInstance?
    # The default prototypes could just invoke each other..
    # def execute_config()
    # def finished(self, action):

    def action_event(self, action, event):
        """
        Default ActionEvent handler

        This function is called when an ActionEvent occurs
        for any submitted Actions. For example, when the Action
        begins or has finished execution.
        """
        if event.type == ActionEvent.FINISH:
            if event.result != 0:
                self.log.error(str(action.builder.__class__.__name__) + \
                             " terminated with unexpected exit status " + \
                               str(event.result) + " -- aborting")
                sys.exit(event.result)

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
        if os.path.exists(path + os.sep + "__init__.py") and path not in sys.path:
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

                # Import the builder as a module
                module = importlib.import_module(name)

                # TODO: a plugin could have multiple builders?
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
