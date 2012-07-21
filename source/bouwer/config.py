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
import configparser

##
# Parse configuration in the given file
# @param filename Path to the configuration file
# @return Reference to the generated configuration
##
def parse(args):

    # Output message
    if args.verbose:
        print(sys.argv[0] + ': reading `' + args.config + '\'')

    # Config file must be readable
    try:
        os.stat(args.config)
    except OSError as e:
        print(sys.argv[0] + ": could not read config file '" + args.config + "': " + str(e))
        sys.exit(1)

    # Parse the given file
    conf = configparser.ConfigParser(interpolation = configparser.ExtendedInterpolation())
    conf.read(args.config)
    return conf
