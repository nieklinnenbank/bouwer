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

##
# Configure using ncurses
#
class MenuConfig:

    ##
    # Constructor
    #
    def __init__(self, core):
        core.register_configurator(self)

    ##
    # See if we have ncurses installed
    #
    def exists():
        # Look for the ncurses module
        return True

    ##
    # See if we have the mkisofs/genisoimage command
    # If we don't have any valid configuration, we are disabled.
    #
    def detect(conf):
        pass

    ##
    # Generate an ISO image
    #
    # @param filename Name of the image
    #
    def execute(self, filename):
        pass
