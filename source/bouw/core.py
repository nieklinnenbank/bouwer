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
import sys
import bouw.config
import bouw.default
import bouw.environment
import bouw.action

#
# Execute the given target in all directories
#
def execute(target = bouw.default.target):

    # Traverse current directory to the top-level Bouwfile
    while os.path.exists('../' + bouw.default.script_filename):
        os.chdir(os.getcwd() + '/../')

    # Parse configuration
    conf = bouw.config.parse(bouw.default.config_filename)

    # Initialize action tree
    action_tree = bouw.action.ActionTree()

    # Traverse directory tree for each configured environment
    if len(conf.sections()) >= 1:
        for section_name in conf.sections():
            env = bouw.environment.Environment(section_name, conf, action_tree)
            env.register_targets(target)

    # Use the default if not any environments configured
    else:
        env = bouw.environment.Environment('DEFAULT', conf, action_tree)
        env.register_targets(target)

    # TODO: actually build a dependency tree

    # Now execute the registered targets in parallel

    # First execute all CC and AS tasks, since they are independent
    # Then execute all LD tasks, since they depend on the CC and AS tasks
    # Finally, do all other things, like building an ISO and filesystem images
