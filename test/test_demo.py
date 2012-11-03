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

import common
import sys
import os
import os.path
import inspect
import unittest
import logging

import bouwer.cli
import bouwer.plugin
import bouwer.config
import bouwer.builder
import bouwer.action

def demo(path):
    def demo_set_path(cls):
        cls.path = path
        return cls
    return demo_set_path

class DemoClass(common.BouwerTester):

    def setUp(self):
        super(DemoClass, self).setUp()

        os.chdir(self.demodir + os.sep + self.path)

        # Reset singletons
        bouwer.config.Configuration.Destroy()
        bouwer.builder.BuilderManager.Destroy()

        # Create command line interface object
        # TODO: ugly hack!
        sys.argv = [ "bouw", "--quiet" ]
        self.cli = bouwer.cli.CommandLine()

        # (Re)load configuration
        self.conf = bouwer.config.Configuration.Instance(self.cli)

        # Load all plugins
        self.plugins = bouwer.plugin.PluginLoader(self.conf)
        self.conf.args = self.cli.parse()

        # Initialize the builder manager
        self.build = bouwer.builder.BuilderManager.Instance(self.conf, self.plugins)

        # Initialize action tree
        self.actions = bouwer.action.ActionManager(self.conf.args, self.plugins)

        # Use the default tree
        self.build.execute_target('build', self.conf.trees.get('DEFAULT'), self.actions)

class DemoTester(common.BouwerTester):
    """
    Tests running Bouwer on the demo projects
    """

    def test_build(self):
        """ Try to invoke the build target of each demo """

        # TODO: please use bouwer modules directly instead? e.g. bouwer.execute()

        for lang in os.listdir(self.demodir):
            for demo in os.listdir(self.demodir + os.sep + lang):
                os.chdir(self.demodir + os.sep + lang + os.sep + demo)

                if os.path.exists('generate.py'):
                    import generate
                    generate.generate()

                result = os.system(self.bouwer + ' -qf')
                self.assertEqual(result, 0, 'building ' + os.getcwd() + ' failed')
                result = os.system(self.bouwer + ' -c')
                self.assertEqual(result, 0, 'cleaning ' + os.getcwd() + ' failed')

                # TODO: assert that the targets are there!

@demo('c/hello')
class HelloTester(DemoClass):

    def test_hello_config(self):
        """ Verify configuration of Hello World """
        pass

    def test_hello_actions(self):
        """ Verify actions of Hello World """
        pass

    def test_hello_compile(self):
        """ Verify compilation of Hello World """
        self.actions.run()

    def _foo_test_hello(self):
        """ Verify correct compilation of Hello World """
        pass

