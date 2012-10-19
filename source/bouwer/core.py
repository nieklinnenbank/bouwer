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
Bouwer core functionality
"""

import os
import os.path
import sys
import logging
import bouwer.cli
import bouwer.plugin
import bouwer.config
import bouwer.builder
import bouwer.action

def execute():
    """
    Execute Bouwfiles with the current configuration
    """

    # Traverse current directory to the top-level Bouwfile
    while os.path.exists('..' + os.sep + 'Bouwfile'):
        os.chdir(os.getcwd() + os.sep + '..' + os.sep)

    # Create command line interface object
    cli = bouwer.cli.CommandLine()

    # Initialize logging
    logging.basicConfig(
        format   = '[%(asctime)s] [%(name)s] %(levelname)s -- %(message)s',
        level    = getattr(logging, cli.args.log_level),
        filename = cli.args.log )

    # (Re)load configuration
    conf = bouwer.config.Configuration.Instance(cli)

    # Load all plugins
    plugins = bouwer.plugin.PluginLoader(conf)

    # Generate final list of command line arguments

    # TODO: we probably want to output the list of possible targets in the help too!
    # documented using PyDoc :-) Fancy!
    
    # e.g. overwrite the print_help() method of argparse:
    # http://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argu

    # OR: we let buildermanager initialize first somehow and then e.g. build.target_list()
    # BUT: buildermanager also needs the final conf.args...
    
    conf.args = cli.parse()

    # If we have a configuration plugin enabled by cli, invoke it
    conf_plugin = None
    try:
        conf_plugin = conf.args.config_plugin
    except AttributeError:
        pass

    if conf_plugin is not None:
        sys.exit(conf_plugin.configure(conf))

    # Initialize the builder manager
    build = bouwer.builder.BuilderManager.Instance(conf, plugins)

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

    # Execute each target in turn.
    for target in conf.args.targets:

        # Initialize action tree
        actions = bouwer.action.ActionManager(conf.args, plugins)

        # TODO: generate an error if no targets are executed.

        # Traverse Bouwfiles for each custom tree
        if len(conf.trees) > 1:
            for tree_name, tree in conf.trees.items():
                if tree_name is not 'DEFAULT' and tree.value():
                    build.execute_target(target, tree, actions)

        # Use the default tree
        else:
            build.execute_target(target, conf.trees.get('DEFAULT'), actions)

        # Dump the generated actions
        if conf.args.verbose:
            actions.dump()

        # Execute the generated actions or perform cleanup
        if conf.args.clean:
            actions.clean()
        else:
            actions.run()

