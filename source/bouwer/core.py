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
import argparse
import bouwer.config
import bouwer.environment
import bouwer.action
import bouwer.work

#
# Parse command line arguments
#
def _parse_arguments():

    # Build parser
    parser = argparse.ArgumentParser(description='Bouwer build automation tool.',
                                     epilog='Copyright (c) 2012 Niek Linnenbank.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', action='version', version='0.0.1')
    parser.add_argument('-v', '--verbose', help='Output verbose build information', action='store_true')
    parser.add_argument('-f', '--force', help='Force a rebuild of all targets', action='store_true')
    parser.add_argument('-c', '--config', help='Location of the configuration file', type=str, default='build.conf')
    parser.add_argument('-s', '--script', help='Filename of scripts containing Actions', type=str, default='Bouwfile')
    parser.add_argument('targets', metavar='TARGET', type=str, nargs='*', default=['build'], help='Build targets to execute')

    # Execute parser
    return parser.parse_args()

#
# Execute the given target in all directories
#
def execute():

    # Parse command line arguments
    args = _parse_arguments()

    # Traverse current directory to the top-level Bouwfile
    while os.path.exists('../' + args.script):
        os.chdir(os.getcwd() + '/../')

    # Parse configuration
    # TODO: please merge the build.conf and argparse stuff!?
    conf = bouwer.config.parse(args)

    # Execute each target in turn.
    for target in args.targets:

        # Initialize action tree
        action_tree = bouwer.action.ActionTree()

        # Traverse directory tree for each configured environment
        if len(conf.sections()) >= 1:
            for section_name in conf.sections():
                env = bouwer.environment.Environment(section_name, conf, args, action_tree)
                env.register_targets(target)

        # Use the default if not any environments configured
        else:
            env = bouwer.environment.Environment('DEFAULT', conf, args, action_tree)
            env.register_targets(target)

        # Execute the generated actions
        master = bouwer.work.Master(action_tree, conf, args)
        master.execute()
