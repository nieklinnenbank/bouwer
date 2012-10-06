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
from bouwer.config import *

class Library(Plugin):
    """ Build a software library """

    def execute(self, target, sources):
        """
        Builder implementation for Library()
        """
        if type(target) is Config and target.value():
            libname = target.keywords.get('library', target.name.lower())

            # Look for optional sources in our child config items
            for child_name in target.keywords.get('childs', []):
                child = self.get_item(child_name)

                if child.type == bool and child.value() and 'source' in child.keywords:
                    sources.append(child.keywords.get('source'))

        elif type(target) is str:
            libname = target
        else:
            raise Exception('Library target must be string or Config')

        cc = self.get_item('CC')
        compiler = self.get_item(cc.value())

        objects = []

        # TODO: ask the build manager for the path to our invocation.
        # then, if a BUILDROOT is set, we should put the object there.
        # otherwise, put the object in this directory.
        # optionally, if a BUILDPATH is set, put the object in this directory,
        # plus the BUILDPATH appended to it (e.g. bld directory @ ASML)
        # TODO: provide a generic mechanism for this!
        for src in sources:
            objects.append(self.Object(src))

        # TODO: replace this with action() instead?
        self.action(libname + '.a', objects,
                    compiler.keywords.get('ar') + ' ' +
                    compiler.keywords.get('arflags') + ' ' + libname + '.a ' +
                    ' '.join(objects))

