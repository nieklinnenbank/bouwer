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
from bouwer.plugin import *

##
# Make an ISO image
#
class Iso(Plugin):

    ##
    # Builders always exist.
    #
    def exists():
        return True

    ##
    # See if we have the mkisofs/genisoimage command
    # If we don't have any valid configuration, we are disabled.
    #
    def inspect(conf):
        pass

    ##
    # Generate an ISO image
    #
    # @param target Name of the image or a Config item.
    # @param sources List of files to include in the ISO.
    #
    def execute(self, target, sources):
        print('Iso.execute(' + str(target) + ',' + str(sources) + ')')
