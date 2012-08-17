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
def load_path(path, cli):

    # The path must exist, otherwise don't attempt
    if not os.path.exists(path):
        return

    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            # TODO: only in verbose mode, but the parser isn't executed yet?
            if cli.args.verbose:
                print('Loading ' + str(filename))
