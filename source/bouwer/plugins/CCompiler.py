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
import glob
from bouwer.plugin import *
from bouwer.builder import *
from bouwer.config import *
import bouwer.util

class Object(Plugin):
    """
    Build an executable object for a program.
    """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'LINK_LIBRARIES', 'CONFIG' ]

    def config_output(self):
        """ Configuration output items """
        return [ 'OBJECTS' ]

    def execute_source(self, source):
        """
        Build an executable object given its `source` file
        """
        CCompiler.Instance().c_object(source)

    def execute_config(self, item, sources):
        """
        Build executable objects if configurion item `item` is True
        """
        if item.value():
            for source in sources:
                self.execute_source(source, item)

class Program(Plugin):
    """
    Build an executable program
    """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'LINK_LIBRARIES', 'CHECK', 'CONFIG' ]

    def execute_config(self, item, sources):
        """
        Build a program given a :class:`.Config` `item` and `sources` list.
        """
        # TODO: also support the program = keyword, like library =
        if item.value():
            CCompiler.Instance().c_program(TargetPath(item.name.lower()), sources, item)

    def execute_target(self, target, sources):
        """
        Build an program given its `target` name and `sources` list
        """
        CCompiler.Instance().c_program(target, sources)

class Library(Plugin):
    """ Build a software library """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'CHECK', 'CONFIG', 'LIBRARY_OBJECTS' ]

    def config_output(self):
        """ Configuration output items """
        return [ 'LIBRARIES' ]

    def execute_config(self, item, sources):
        """
        Build a library using a :class:`.Config` and list of `sources`
        """
        if not item.value():
            return

        target = item.get_key('library', item.name.lower())
        CCompiler.Instance().c_library(TargetPath(target), sources, item)

    def execute_target(self, target, sources):
        """
        Build a library using a `target` name and list of `sources`
        """
        CCompiler.Instance().c_library(target, sources)

class LibraryObject(Plugin):
    """
    Specify an additional object for a library
    """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'CONFIG' ]

    def config_output(self):
        """ Configuration output items """
        return [ 'LIBRARY_OBJECTS' ]

    def execute_source(self, source):
        """
        Build an executable object given its `source` file
        """
        compiler.CCompiler.Instance().c_object(source)

    def execute_config(self, item, sources):
        """
        Build executable objects if configurion item `item` is True
        """
        if item.value():
            for source in sources:
                CCompiler.Instance().c_object(source, item)

class UseLibrary(Plugin):
    """
    Build and link a program against a library
    """

    def config_input(self):
        """ Configuration input items """
        return [ 'CC', 'LIBRARIES', 'OBJECTS' ]

    def config_output(self):
        """ Configuration output items """
        return [ 'LINK_LIBRARIES' ]

    def execute_config_params(self, item, libsrc):
        if item.value():
            self.execute_any(libsrc)

    def execute_any(self, libraries, target = None):
        """
        Build against a :py:`list` of `libraries`

        The library target for linking will be discovered internally.
        """
        CCompiler.Instance().use_library(libraries, target)

class CCompiler(bouwer.util.Singleton):

    def __init__(self):
        """
        Constructor
        """
        self.conf  = Configuration.Instance()
        self.build = BuilderManager.Instance()
        self.c_object_list = []
        self.libraries  = {}
        self.use_libraries = {}
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

    def _get_libraries_for_target(self, target):
        treedict  = self.use_libraries.get(self.conf.active_tree, {})
        dirdict   = treedict.get(self.conf.active_dir, {})
        use_libs  = dirdict.get(target.absolute, [])
        use_libs += dirdict.get(None, [])
        return use_libs

    def c_object(self, source, item = None, **extra_tags):
        """
        Compile a C source file into an object file
        """
        chain     = self.conf.active_tree.get('CC')
        cc        = self.conf.active_tree.get(chain.value())
        splitfile = os.path.splitext(source.relative)
        incflags  = ''

        if splitfile[1] != '.c':
            raise Exception('not a C source file: ' + source)

        # Translate source and target paths relative from project-root
        outfile = TargetPath(splitfile[0] + '.o')

        # Link the config item and its parents to this target file.
        if item is not None:
            self._register_config_deps(outfile, item)
        elif not extra_tags.get('standalone', False):
            self.c_object_list.append(outfile)

        # Add C preprocessor paths
        try:
            for path in (cc.get_key('incpath', '').split(':') + chain.get_key('incpath', '').split(':')):
                if path: incflags += cc['incflag'] + path + ' '
        except KeyError:
            pass

        # Add C preprocessor paths from libraries
        for libname in self._get_libraries_for_target(outfile):
            try:
                incflags += cc['incflag'] + self.libraries[self.conf.active_tree][libname][1] + ' '
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

    def c_program(self, target, sources, item = None, **extra_tags):
        """
        Build an program given its `target` name and `sources` list
        """

        # Retrieve compiler chain
        chain   = self.conf.get('CC')
        cc      = self.conf.get(chain.value())
        ldpath  = ''
        ldflags = cc['ldflags']
        incpath = ''
        objects = self._lookup_config_deps(item) + self.c_object_list
        extra_deps = []

        # Add linker paths
        for path in cc['ldpath'].split(':'):
            if path: ldpath += cc['ldflag'] + path + ' '

        for libname in self._get_libraries_for_target(target):
            # Local library?
            try:
                lib = self.libraries[self.conf.active_tree][libname][0]
                ldpath += cc['ldflag'] + os.path.dirname(lib.absolute) + ' '
                extra_deps.append(lib)
            except KeyError:
                pass

            # Link with the library
            if libname[:3] == 'lib':
                libname = libname[3:]

            ldflags += ' -l' + libname

        # Traverse all source files given
        for source in sources:
            objects.append(self.c_object(source, **extra_tags))

        # Set our pretty name
        if 'pretty_name' not in extra_tags:
            extra_tags['pretty_name'] = 'LINK'

        # Link the program
        self.build.action(target, objects + extra_deps,
                          cc['ld'] + ' ' + str(target) + ' ' +
                         (' '.join([str(o) for o in objects])) + ' ' + ldpath +
                          ldflags + ' ' + cc['ldscript'],
                         **extra_tags)

        # Clear list of objects
        self.c_object_list = []  # TODO: do we still need this???

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
        if self.conf.active_tree not in self.libraries:
            self.libraries[self.conf.active_tree] = {}

        self.libraries[self.conf.active_tree][libname] = (target, self.conf.active_dir)

    def use_library(self, libraries, target = None):
        """
        Build against a :py:`list` of `libraries`

        The library target for linking will be discovered by
        searching the generated :class:`.Action` objects in
        the actions layer.
        """
        if target: target = target.absolute

        use_lib_tree   = self.use_libraries.setdefault(self.conf.active_tree, {})
        use_lib_dir    = use_lib_tree.setdefault(self.conf.active_dir, {})
        use_lib_target = use_lib_dir.setdefault(target, [])
        use_lib_target += libraries
