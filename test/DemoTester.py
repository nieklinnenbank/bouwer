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
import os.path
import inspect
import unittest

class DemoTester(common.BouwerTester):
    """
    Tests running Bouwer on the demo projects
    """

    def test_build(self):
        """ Try to invoke the build target of each demo """

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

