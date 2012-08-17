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
import os.path
import inspect

##
# Represents a loadable Bouwer plugin
#
class Plugin:

    ##
    # Constructor
    #
    def __init__(self):
        pass

    ##
    # Check to see if this module has all external dependencies
    #
    def exists(self):
        return True

##
# Load all plugins in the given directory
#
class PluginLoader:

    def __init__(self, conf):

        self.conf = conf

        # TODO: ugly long code!!!
        core_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        base_path = os.path.dirname(os.path.abspath(core_path + '..' + os.sep + '..' + os.sep))
        plug_path = base_path + os.sep + 'source' + os.sep + 'bouwer-plugins'

        self._load_path(plug_path)
        self._load_path(conf.args.plugin_dir)

    def _load_path(self, path):

        # The path must exist, otherwise don't attempt
        if not os.path.exists(path):
            return

        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:

                # Skip non python files
                if not filename.endswith(".py") or not filename[0].isupper():
                    continue

                # Debug out
                if self.conf.args.verbose:
                    print('Loading ' + path + os.sep + str(filename))

                # Load the module
                exec(compile(open(path + os.sep + filename).read(), filename, 'exec'))

                # Import the builder as a module
                #module = importlib.import_module('bouwer.builder.' + name)
                #class_ = getattr(module, name)
                #instance = class_(self)

                # Add the execute function to ourselves
                #setattr(self.__class__, name, instance.execute)
