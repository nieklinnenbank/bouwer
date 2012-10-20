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
import pylint.lint
import sys
import glob
import common

class StaticTester(common.BouwerTester):
    """
    Runs static code analyzer tools on Bouwer source code
    """

    def _get_srclist(self):
        srclist  = glob.glob(self.srcdir + os.sep + 'bouwer' + os.sep + '*.py')
        srclist += glob.glob(self.srcdir + os.sep + 'bouwer' + os.sep + 'plugins' + os.sep + '*.py')
        return srclist

    def test_pep8(self):
        """
        Run the pep8 code style checker on the bouwer code
        """
        pass

    def test_pyflakes(self):
        """
        Run pyflakes on the bouwer code
        """
        self.assertEqual(os.system('pyflakes ' + ' '.join(self._get_srclist())), 0,
                        'PyFlakes must be successful')

    def test_pychecker(self):
        """
        Run pychecker on the bouwer code
        """
        srclist = self._get_srclist()
        pypath = 'PYTHONPATH=' + os.environ.get('PYTHONPATH', '') + self.srcdir
        result = os.system(pypath + ' pychecker --limit=1000 ' + ' '.join(srclist))
        self.assertEqual(result, 0, 'PyChecker must be successful')

    def test_pylint(self):
        """
        Run pylint on the bouwer code
        """
        for filename in os.listdir(self.srcdir):
            try:
                pylint.lint.Run(['--reports=n', '--output-format=parseable',
                                 '--disable=E1003', '--min-public-methods=1',
                                  filename])
            except SystemExit as e:
                self.assertEqual(e.code, 0, 'PyLint must be successful')
