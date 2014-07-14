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
from bouwer.util import *

""" Global list of objects compiled """
c_object_list = []

def _find_headers(source, paths):
    """
    Find headers included by a C file.
    Return them as a list.
    """

    # TODO: make this recursive
    # TODO: look in the paths!!!!

    # Retrieve cache and file stat
    cache = Cache.Instance('c_headers')
    st = os.stat(source.absolute)
    headers = []
    headers_str = []
    
    # Do we have the file still in an up-to-date cache?
    if cache.timestamp() >= st.st_mtime and cache.get(source.absolute) is not None:
        for hdr in cache.get(source.absolute):
            headers.append(SourcePath(hdr))
        return headers

    fp = open(source.absolute, "r")
    for line in fp.readlines():
        idx = line.find('#include')
        if idx == -1:
            continue

        if line.find('<') != -1:
            header_name = line.split('<')[1].split('>')[0]
        else:
            header_name = line.split('"')[1]

        try:
            # TODO: try to find it in any of the paths too....
            sourcepath = SourcePath(header_name)

            os.stat(sourcepath.absolute)
            headers.append(sourcepath) # TODO: only if in current dir...
            headers_str.append(sourcepath.absolute)

        except Exception as e:
            pass

    # Update the cache. Finish up.
    fp.close()
    cache.put(source.absolute, headers_str)
    return headers

def c_object(source, **extra_tags):
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

        try:
            for path in cc['incpath'].split(':'):
                if len(path) > 0:
                    incflags += cc['incflag'] + path + ' '
        except KeyError:
            pass

        # Determine dependencies to build output file.
        deps = _find_headers(source, cc['incpath'].split(':'))
        deps.append(source)

        # Set our pretty name
        if 'pretty_name' not in extra_tags:
            extra_tags['pretty_name'] = 'CC'

        # Register compile action
        build.action(outfile, deps,
                     cc['cc'] + ' ' +
                     str(outfile) + ' ' +
                     cc['ccflags'] + ' ' + incflags +
                     str(source),
                     **extra_tags
        )

        c_object_list.append(outfile)

        return outfile

    # Unknown filetype
    else:
        raise Exception('unknown filetype: ' + source)

