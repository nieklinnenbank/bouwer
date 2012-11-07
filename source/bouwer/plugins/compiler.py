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
from bouwer.plugin import *
from bouwer.builder import *
from bouwer.config import *

def c_object(source):
    """
    Compile a C source file into an object file
    """
    config = Configuration.Instance()
    build  = BuilderManager.Instance()
    chain  = config.active_tree.get('CC')
    cc     = config.active_tree.get(chain.value())
    splitfile = os.path.splitext(source.relative)

    if splitfile[1] == '.c':

        # Translate source and target paths relative from project-root
        outfile = TargetPath(splitfile[0] + '.o')

        # Add C preprocessor paths
        incflags = ''
        for path in cc.keywords.get('incpath'):
            incflags += cc.keywords.get('incflag') + path + ' '

        # Register compile action
        build.action(outfile, [ source ],
                     cc.keywords.get('cc') + ' ' +
                     str(outfile) + ' ' +
                     cc.keywords.get('ccflags') + ' ' + incflags +
                     str(source))
        return outfile

    # Unknown filetype
    else:
        raise Exception('unknown filetype: ' + source)

