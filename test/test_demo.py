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
import subprocess

import bouwer.cli
import bouwer.plugin
import bouwer.config
import bouwer.builder
import bouwer.action

def demo(path):
    """
    This class annotation sets the `path` member in the class.
    """

    def demo_set_path(cls):
        cls.path = path
        return cls
    return demo_set_path

class DemoClass(common.BouwerTester):
    """
    Tester class for Bouwer demo projects
    """

    def setUp(self):
        """
        Runs before every test case
        """
        super(DemoClass, self).setUp()

        self.demopath = self.demodir + os.sep + self.path
        os.chdir(self.demopath)

        # Reset singletons
        bouwer.config.Configuration.Destroy()
        bouwer.builder.BuilderManager.Destroy()
        bouwer.plugin.PluginManager.Destroy()

        # Create command line interface object
        # TODO: ugly hack!
        sys.argv = [ "bouw", "--quiet" ]
        self.cli = bouwer.cli.CommandLine()

        # (Re)load configuration
        self.conf = bouwer.config.Configuration.Instance(self.cli)

        # Initialize the builder manager
        self.build = bouwer.builder.BuilderManager.Instance()

        # Load all plugins
        self.plugins = bouwer.plugin.PluginManager.Instance()
        self.conf.args = self.cli.parse()

        # Clean first
        self.cli.args.clean = True
        self.build.execute('build', self.conf.trees.get('DEFAULT'))

        # Execute with the default tree
        self.cli.args.clean = False
        self.build.execute('build', self.conf.trees.get('DEFAULT'))

    def _run_prog(self, prog):
        """ Run the given demo program """
        return subprocess.check_output(self.demopath + os.sep + prog).decode('utf-8')

# TODO: these tests do not catch the problem when the targets are already there
# from a previous run, but due to a change, are not compiled anymore. Then the run_prog()
# tests succeed.. Please verify.

class DemoTester(common.BouwerTester):
    """
    Tests running Bouwer on the demo projects
    """

    # TODO: this test is obsolete. A part of it might go in the test_cli.py.

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
    """ Tests for the Hello World demo """

    def test_hello_config(self):
        """ Verify configuration of Hello World """
        self.assertEqual(self.conf.get('HELLOMSG').value(), "Hello World!")
        self.assertTrue(self.conf.get('HELLO').value())

    def test_hello_actions(self):
        """ Verify actions of Hello World """
        pass

    def test_hello_compile(self):
        """ Verify compilation of Hello World """
        self.assertEqual(self._run_prog('hello'), "Hello World!\n")

@demo('c/library')
class LibraryTester(DemoClass):
    """ Tests for the Library builder demo """

    def test_library_config(self):
        """ Verify configuration of the Library demo """
        self.assertTrue(self.conf.get('LIBFUZZ').value())
        self.assertTrue(self.conf.get('LIBDUMMY').value())
        self.assertTrue(self.conf.get('LIBDUMMY_FOO').value())
        self.assertTrue(self.conf.get('LIBDUMMY_BAR').value())
        self.assertTrue(self.conf.get('LIBDUMMY_UTIL').value())

    def test_library_actions(self):
        """ Verify actions of the Library demo """
        pass

    def test_library_compile(self):
        """ Verify compilation of the Library demo """
        self.assertEqual(self._run_prog('myprog' + os.sep + 'myprog'), 'int=0 fuzz=1\n')

@demo('c/override')
class OverrideTester(DemoClass):
    """ Tests for the Config override demo """

    def test_override_config(self):
        """ Verify configuration of override demo """
        self.assertTrue(self.conf.get('HELLO1').value())
        self.assertEquals(self.conf.get('HELLOMSG1').value(), 'Hello World 1!')

        self.conf.active_dir = './hello1'
        self.assertTrue(self.conf.get('GCC'))
        self.assertEquals(self.conf.get('GCC').get_key('ccflags'), '-c -O3')

        self.conf.active_dir = './hello2'
        self.assertTrue(self.conf.get('GCC'))
        self.assertTrue(self.conf.get('HELLO2'))
        self.assertEquals(self.conf.get('HELLOMSG2').value(), 'Hello World 2!')

    def test_override_compile(self):
        """ Verify compilation of override demo """
        self.assertEqual(self._run_prog('hello1/hello1'), "Hello World 1!\n")
        self.assertEqual(self._run_prog('hello2/hello2'), "Hello World 2!\n")

