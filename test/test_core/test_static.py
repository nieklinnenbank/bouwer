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
import glob
import unittest
import subprocess
from test import *

class StaticTester(BouwerTester):
    """
    Runs static code analyzer tools on Bouwer source code
    """

    def _get_srclist(self):
        """ Get a list of bouwer source files """
        return [ self.srcdir + os.sep + 'bouwer' + os.sep + 'config.py' ]

        #srclist  = glob.glob(self.srcdir + os.sep + 'bouwer' + os.sep + '*.py')
        #srclist += glob.glob(self.srcdir + os.sep + 'bouwer' + os.sep + 'plugins' + os.sep + '*.py')
        #return srclist

    def _program_exists(self, args):
        """ Check if the given program exists on the system """
        try:
            null = open(os.devnull, "w")
            p = subprocess.Popen(args, stdout = null, stderr = null)
            null.close()

        except OSError:
            self.skipTest(args[0] + ' not installed')

    @unittest.skip('temporary disabled until code fixed')
    def test_pep8(self):
        """
        Run the pep8 code style checker on the bouwer code
        """
        self._program_exists(['pep8'])
        self.assertEqual(os.system('pep8 --repeat ' + ' '.join(self._get_srclist())), 0,
                        'PEP8 must be successful')

    @unittest.skip('temporary disabled until code fixed')
    def test_pyflakes(self):
        """ Run pyflakes on the bouwer code """
       
        self._program_exists(['pyflakes', '/asdfasfasfasfasf'])
        self.assertEqual(os.system('pyflakes ' + ' '.join(self._get_srclist())), 0,
                        'PyFlakes must be successful')

    @unittest.skip('temporary disabled until code fixed')
    def test_pychecker(self):
        """ Run pychecker on the bouwer code """

        self._program_exists(['pychecker'])

        srclist = self._get_srclist()

        pypath = 'PYTHONPATH=' + os.environ.get('PYTHONPATH', '') + self.srcdir
        pyargs = '--limit=1000 --no-argsused --moduledoc --classdoc --funcdoc ' + \
                 '--changetypes --constant1 --callattr --initattr --no-isliteral -Q '

        result = os.system(pypath + ' pychecker ' + pyargs + ' '.join(srclist))
        self.assertEqual(result, 0, 'PyChecker must be successful')

    @unittest.skip('temporary disabled until code fixed') 
    def test_pylint(self):
        """
        Run pylint on the bouwer code
        """

        try:
            import pylint.lint
        except ImportError:
            self.skipTest('PyLint not installed')

        for filename in os.listdir(self.srcdir):
            try:
                pylint.lint.Run(['--reports=n', '--output-format=parseable',
                                 '--disable=E1003', '--min-public-methods=1',
                                  filename])
            except SystemExit as e:
                self.assertEqual(e.code, 0, 'PyLint must be successful')

    def test_todos(self):
        """
        Search for TODO entries in bouwer code
        """
        self.skipTest('implement')

