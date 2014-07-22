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
import bouwer.util

#TODO: i want the Program, Object, Library, etc builders in this file. and call it CCompiler.py

class CCompiler(bouwer.util.Singleton):

    def __init__(self):
        """
        Constructor
        """
        self.conf  = Configuration.Instance()
        self.build = BuilderManager.Instance()
        self.c_object_list = []
        self.objects_for_items = {}

    def _find_headers(self, source, paths):
        """
        Find headers included by a C file.
        Return them as a list.
        """

        # TODO: make this recursive
        # TODO: look in the paths!!!!

        # Retrieve cache and file stat
        cache = bouwer.util.Cache.Instance('c_headers')
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

    def _find_config_deps(self, item):
        dep_list = [ item ]
        for dep in item.get_key('depends', []):
            dep_list += self._find_config_deps(self.conf.get(dep))

        return dep_list

    def _register_config_deps(self, outfile, item):
        """
        Make a list of objects to output as dependency for the given item
        Used in e.g. if the item is set for c_library/c_program. Then the outfile
        is automatically added as dependency of the library/program.
        """
        deps      = self._find_config_deps(item)
        tree_name = self.conf.active_tree.name

        for dep in deps:
            slot_name = tree_name + '.' + dep.name

            if slot_name not in self.objects_for_items:
                self.objects_for_items[slot_name] = []

            self.objects_for_items[slot_name].append(outfile)
        return deps

    def _lookup_config_deps(self, item):
        if item is not None:
            tree_name = self.conf.active_tree.name
            slot_name = tree_name + '.' + item.name
            return self.objects_for_items.get(slot_name, [])
        else:
            return []

    def c_object(self, source, item = None, **extra_tags):
        """
        Compile a C source file into an object file
        """
        chain  = self.conf.active_tree.get('CC')
        cc     = self.conf.active_tree.get(chain.value())
        splitfile = os.path.splitext(source.relative)

        if splitfile[1] == '.c':

            # Translate source and target paths relative from project-root
            outfile = TargetPath(splitfile[0] + '.o')

            if item is not None:
                deps = self._register_config_deps(outfile, item)
            else:
                self.c_object_list.append(outfile)

            # Add C preprocessor paths
            incflags = ''

            try:
                for path in cc['incpath'].split(':'):
                    if len(path) > 0:
                        incflags += cc['incflag'] + path + ' '
            except KeyError:
                pass

            # Determine dependencies to build output file.
            deps = self._find_headers(source, cc['incpath'].split(':'))
            deps.append(source)

            # Set our pretty name
            if 'pretty_name' not in extra_tags:
                extra_tags['pretty_name'] = 'CC'

            # Register compile action
            self.build.action(outfile, deps,
                         cc['cc'] + ' ' +
                         str(outfile) + ' ' +
                         cc['ccflags'] + ' ' + incflags +
                         str(source),
                         **extra_tags
            )

            return outfile

        # Unknown filetype
        else:
            raise Exception('unknown filetype: ' + source)

    def c_program(self, target, sources, item = None):
        """
        Build an program given its `target` name and `sources` list
        """

        # Retrieve compiler chain
        chain = self.conf.get('CC')
        cc    = self.conf.get(chain.value())
        objects = []

        extra_deps = self._lookup_config_deps(item) + self.c_object_list

        # TODO: we dont need to do it like this anymore. Just save it in a member....
        if self.conf.get('SOURCES') is not None:
            extra_deps += self.conf.get('SOURCES').value()

        # Traverse all source files given
        for source in sources:
            objects.append(self.c_object(source))

        # Add linker paths
        ldpath = ''
        for path in cc['ldpath'].split(':'):
            if len(path) > 0:
                ldpath += cc['ldflag'] + path + ' '

        # TODO: use the compiler.c_object_list 

        # Link the program
        self.build.action(target,
                          objects + extra_deps, 
                          cc['ld'] + ' ' + str(target) + ' ' +
                         (' '.join([str(o) for o in objects])) + ' ' + ldpath +
                          cc['ldflags'] + ' ' + cc['ldscript'],
                          pretty_name='LINK')

    def c_library(self, target, sources, item = None):
        """
        Build a library using a `target` name and list of `sources`
        """

        chain = self.conf.get('CC')
        cc = self.conf.get(chain.value())
        libname = str(target.relative)
        # TODO: do we really need c_object_list here.... we already know the sources. Only Object() stuff
        # needs to be discovered by the config deps lookup...
        target.append('.a')

        # Generate actions to build the library objects
        for src in sources:
            self.c_object(src)

        extra_deps = self._lookup_config_deps(item) + self.c_object_list

        # Generate action for linking the library
        self.build.action(target, extra_deps,
                          cc['ar'] + ' ' +
                          cc['arflags'] + ' ' + str(target) + ' ' +
                        (' '.join([str(o) for o in extra_deps])),
                          pretty_name='LIB')

        # Clear C object list
        self.c_object_list = []

        # Publish ourselves to the libraries list
        if self.conf.active_tree.get('LIBRARIES') is None:
            # TODO: why do i need to specify active_tree here...
            self.conf.active_tree.add(Config('LIBRARIES', {}, temporary = True),
                                      Configuration.Instance().base_conf) # TODO: path is an ugly hack...

        # Add ourselve to the libraries dictionary
        libdict = self.conf.get('LIBRARIES').value()
        libdict[libname] = (target, self.conf.active_dir)

    def generate_library_override(self, libraries):
        """
        Build against a :py:`list` of `libraries`

        The library target for linking will be discovered by
        searching the generated :class:`.Action` objects in
        the actions layer.
        """

        # TODO: this should become a *TEMPORARY* per-directory override instead
        chain = self.conf.get('CC')
        cc    = self.conf.get(chain.value())

        # TODO: find the correct libary path using the actions layer!!!
        # TODO: only do it like this if static linking!!!
        # TODO: use keyword indirection instead of copying the original keywords?!
        tmp = ConfigBool(cc.name, **cc._keywords)
        slist = []

        libs = self.conf.get('LIBRARIES')
        if libs is None:
            return
        
        libdict = libs.value()

        # Loop all given libraries
        for lib in libraries:

            target, path = libdict[lib]
            slist.append(target)

            if lib[:3] == 'lib':
                libname = lib[3:]
            else:
                libname = lib

            tmp._keywords['ldpath']  += ':' + os.path.dirname(target.absolute)
            tmp._keywords['incpath'] += ':' + path
            tmp._keywords['ldflags'] += ' -l' + libname + ' '

        self.conf.active_tree.add(tmp)
        self.conf.active_tree.add(Config('SOURCES', slist, temporary = True))
