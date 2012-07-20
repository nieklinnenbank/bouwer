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
import bouwer.config
import bouwer.default
import bouwer.environment
import bouwer.action
import bouwer.work

#
# Execute the given target in all directories
#
def execute(target = bouwer.default.target):

    # Traverse current directory to the top-level Bouwfile
    while os.path.exists('../' + bouwer.default.script_filename):
        os.chdir(os.getcwd() + '/../')

    # Parse configuration
    conf = bouwer.config.parse(bouwer.default.config_filename)

    # Initialize action tree
    action_tree = bouwer.action.ActionTree()

    # Traverse directory tree for each configured environment
    if len(conf.sections()) >= 1:
        for section_name in conf.sections():
            env = bouwer.environment.Environment(section_name, conf, action_tree)
            env.register_targets(target)

    # Use the default if not any environments configured
    else:
        env = bouwer.environment.Environment('DEFAULT', conf, action_tree)
        env.register_targets(target)

    # Execute the generated actions
    master = bouwer.work.Master(action_tree)
    master.execute()

    # Now execute the registered targets in parallel

    # First execute all CC and AS tasks, since they are independent
    # Then execute all LD tasks, since they depend on the CC and AS tasks
    # Finally, do all other things, like building an ISO and filesystem images
