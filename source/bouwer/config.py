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

import sys
import configparser

##
# Parse configuration in the given file
# @param filename Path to the configuration file
# @return Reference to the generated configuration
##
def parse(filename):
    print(sys.argv[0] + ': reading `' + filename + '\'')

    # Parse the given file
    conf = configparser.ConfigParser(interpolation = configparser.ExtendedInterpolation())
    conf.read(filename)
    return conf
