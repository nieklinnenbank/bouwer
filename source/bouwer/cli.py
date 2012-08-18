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
import argparse
import configparser

##
# Represents the command line interface
#
class CommandLine:

    ##
    # Constructor
    #
    def __init__(self):

        # Build parser
        self.parser = argparse.ArgumentParser(description='Bouwer build automation tool.',
                                     epilog='Copyright (c) 2012 Niek Linnenbank.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help = False)
        self.parser.add_argument('--version', action='version', version='0.0.1')
        self.parser.add_argument('-v', '--verbose', help='Output verbose build information', action='store_true', default=False)
        self.parser.add_argument('-f', '--force', help='Force a rebuild of all targets', action='store_true', default=False)
        self.parser.add_argument('-n', '--number', help='Test number argument', type=int, default=123)
        self.parser.add_argument('-d', '--float', help='Test float argument', type=float, default=4.56)
        self.parser.add_argument('-P', '--plugin-dir', help='Directory containing plugins', type=str, default='bouw_plugins')

        # TODO: this must be an "output" module, same as e.g. the "pretty" output module with " CC  foo.c",
        # and the verbose output module with all full commands printed
        self.parser.add_argument('-p', '--progress', help='Print progress bar only at build', action='store_true', default=False)

        self.parser.add_argument('targets', metavar='TARGET', type=str, nargs='*', default=['build'], help='Build targets to execute')

        # Allow the user to override the default arguments using RC files
        self._read_rc()

        # Execute command line parser to retrieve known arguments
        self.args, self.unknowns = self.parser.parse_known_args()

    ##
    # Interpret all command line arguments
    #
    def parse(self):

        # Parse the arguments
        self.parser = argparse.ArgumentParser(parents = [self.parser],
        description='Bouwer build automation tool.',
                                     epilog='Copyright (c) 2012 Niek Linnenbank.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.args = self.parser.parse_args()
#        self.parser.format_help()
        return self.args

    ##
    # Read file(s) containing user-defined cli argument defaults.
    #
    def _read_rc(self):

        # Read any existing RC files
        rc = configparser.ConfigParser()
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
