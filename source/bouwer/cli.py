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
Bouwer command line interface
"""

import os
import os.path
import argparse
import multiprocessing

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

class CommandLine:
    """
    Represents the command line interface to bouwer
    
    TODO: extend somekind of argparse class here
    """

    def __init__(self):
        """ Constructor """
        self.parser = argparse.ArgumentParser(description='Bouwer build automation tool.',
                                     epilog='Copyright (c) 2012 Niek Linnenbank.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help = False)
        self.parser.add_argument('--version', action='version', version='0.1.0')
        self.parser.add_argument('-l', '--log', help='Send logging output to the given file', type=str, default=None)
        self.parser.add_argument('-L', '--log-level', help='Set the logging level', type=str, default='WARNING', choices = [ 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' ])
        self.parser.add_argument('-v', '--verbose', help='alias for -L DEBUG', action='store_true', default=False)
        self.parser.add_argument('-f', '--force', help='Force a rebuild of all targets', action='store_true', default=False)
        self.parser.add_argument('-c', '--clean', help='Remove all targets and generated dependencies', action='store_true', default=False)
        self.parser.add_argument('-P', '--plugin-dir', help='Directory containing plugins', type=str, default='bouw_plugins')
        self.parser.add_argument('-w', '--workers', help='Number of worker processes to start', type=int, default=multiprocessing.cpu_count())
        self.parser.add_argument('targets', metavar='TARGET', type=str, nargs='*', default=['build'], help='Build targets to execute')

        # Allow the user to override the default arguments using RC files
        self._read_rc()

        # Execute command line parser to retrieve known arguments
        self.args, self.unknowns = self.parser.parse_known_args()

        # -v is an alias for -L DEBUG
        if self.args.verbose:
            self.args.log_level = 'DEBUG'

    def parse(self):
        """
        Interpret all command line arguments
        """
        self.parser = argparse.ArgumentParser(parents = [self.parser],
                                     description='Bouwer build automation tool.',
                                     epilog='Copyright (c) 2012 Niek Linnenbank.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.args = self.parser.parse_args()
        return self.args

    def _read_rc(self):
        """
        Read file(s) containing user defined command line argument defaults
        """

        # Read any existing RC files
        rc = ConfigParser()
        rc.read([ os.path.expanduser('~' + os.sep + '.bouwrc'), '.bouwrc'])

        # Set argument defaults
        user_args = dict(rc.items('DEFAULT'))

        # Attempt to type cast booleans, floats and integers
        for user_arg in user_args:

            arg = user_args[user_arg]

            # Boolean
            if arg == 'True' or arg == 'False':
                user_args[user_arg] = bool(arg)
                continue

            # Integer
            try:
                user_args[user_arg] = int(arg)
                continue
            except ValueError:
                pass

            # Float
            try:
                user_args[user_arg] = float(arg)
                continue
            except ValueError:
                pass

        # Set defaults
        self.parser.set_defaults(**user_args)

