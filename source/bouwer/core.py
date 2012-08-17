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
import bouwer.plugin
import bouwer.cli

##
# Execute the given target in all directories
#
def execute():

    # Create command line interface object
    cli = bouwer.cli.CommandLine()

    # Traverse current directory to the top-level Bouwfile
    while os.path.exists('..' + os.sep + cli.args.script):
        os.chdir(os.getcwd() + os.sep + '..' + os.sep)

    # Get the path to this source file
    # TODO: ugly long code!!!
    core_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    base_path = os.path.dirname(os.path.abspath(core_path + '..' + os.sep + '..' + os.sep))
    conf_path = base_path + os.sep + 'config'
    plug_path = base_path + os.sep + 'source' + os.sep + 'bouwer-plugins'

    # Load all plugins from distribution and user defined
    # These plugins may register new command line argument types
    bouwer.plugin.load_path(plug_path, cli)
    bouwer.plugin.load_path(cli.args.plugin_dir, cli)

    # Generate final list of command line arguments
    args = cli.parse()

    # Create configuration object
    conf = bouwer.config.Configuration(args)

    # Parse all pre-defined configurations from Bouwer
    for conf_file in os.listdir(conf_path):
        conf.parse(conf_path + os.sep + conf_file)

    # Parse all user defined configurations
    for dirname, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if filename == cli.args.config:
                conf_file = os.path.join(dirname, filename)
                conf.parse(conf_file)

    # Dump the current configuration for debugging
    if cli.args.verbose:
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
