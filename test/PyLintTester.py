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
import common

class PyLintTester(common.BouwerTester):
    """
    Runs Pylint static code checker on Bouwer
    """
    
    def test_run(self):
        """ Run pylint on the bouwer code """

        for filename in os.listdir(self.srcdir):
            #output = WritableObject()

            try:
                pylint.lint.Run(['--reports=n', '--output-format=parseable',
                                 '--disable=E1003', '--min-public-methods=1',
                                  filename])
            except SystemExit as e:
                self.assertEqual(e.code, 0, 'PyLint must be successful')
