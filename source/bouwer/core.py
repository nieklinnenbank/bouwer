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
import inspect
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
    parser.add_argument('-c', '--config', help='Location of the configuration file', type=str, default='Bouwconfig')
    parser.add_argument('-s', '--script', help='Filename of scripts containing Actions', type=str, default='Bouwfile')

# TODO: this must be an "output" module, same as e.g. the "pretty" output module with " CC  foo.c",
# and the verbose output module with all full commands printed
    parser.add_argument('-p', '--progress', help='Print progress bar only at build', action='store_true')

    parser.add_argument('targets', metavar='TARGET', type=str, nargs='*', default=['build'], help='Build targets to execute')

    # Execute parser
    return parser.parse_args()

def load_modules():
    pass

#
# Execute the given target in all directories
#
def execute():

    # Parse command line arguments
    args = _parse_arguments()

    # Traverse current directory to the top-level Bouwfile
    while os.path.exists('../' + args.script):
        os.chdir(os.getcwd() + '/../')

    # Load all modules
    load_modules()

    # Get the path to this source file
    core_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    base_path = os.path.dirname(os.path.abspath(core_path + '../../'))
    conf_path = base_path + '/config'

    # Parse configuration
    # TODO: please merge the build.conf and argparse stuff!?
    conf = bouwer.config.Configuration(args)

    # Parse all pre-defined configurations
    for conf_file in os.listdir(conf_path):
        conf.parse(conf_path + os.sep + conf_file)

    # Parse all user configurations
    for dirname, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if filename == args.config:
                conf_file = os.path.join(dirname, filename)
                conf.parse(conf_file)

    # Dump the current configuration for debugging
    if args.verbose:
        conf.dump()

    #
    # TODO: the core runs all targets inside a Bouwfile to let them *REGISTER*
    # the possible Actions. Then, only the *ENABLED* targets are run in order.
    # That way, it is possible to derive inter-target dependencies, e.g.:
    #
    # def iso:
    #     Iso('myimage.iso', 'obj_dir')  <- if only iso is given as the target, the build dependencies are also run
    #
    # def build:
    #     Program('foo', 'bar.c')  <- written to obj_dir
    #     Library('zzz', 'asdf.c') <- written to obj_dir
    #

"""
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
"""
