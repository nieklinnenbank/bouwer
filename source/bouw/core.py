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
import sys
import config

#
# Register all targets with the given name by recursing in all directories.
#
def register_targets(target):

    # Look for build.py in all subdirectories
    for dirname, dirnames, filenames in os.walk('.'):
	for filename in filenames:
	    if filename == config.script_name:

		path = os.path.join(dirname, filename)
		print sys.argv[0] + ': parsing `' + path + '\''

	        globs = {}
	        locs  = {}

	        # Parse the build.py file
	        execfile(path, globs, locs)

	        # execute the build target
		if target in locs:
		    locs[target](1)


#
# Execute the given target in all directories
#
def execute_target(target):

    # TODO: import configuration to generate the environments

    # Traverse directory tree to find all instances of the given target
    register_targets(target)

    # TODO: actually build a dependency tree

    # Now execute the registered targets in parallel

    # First execute all CC and AS tasks, since they are independent
    # Then execute all LD tasks, since they depend on the CC and AS tasks
    # Finally, do all other things, like building an ISO and filesystem images
    pass
