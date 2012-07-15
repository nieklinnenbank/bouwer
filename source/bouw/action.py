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

class ActionTree:

    def __init__(self):
        self.buildmap = {}

    def add(self, target, cmd, sources, env):

        print("add(" + target + "," + str(sources) + ")")

        # Honour the buildroot setting
        buildroot = env['buildroot'] + os.sep + env['id']

        # Full path to the target from the top-level Bouwfile
        full_target = os.path.dirname(env.bouwfile) + os.sep + target

        # Real path to the target, using a buildroot
        real_dir    = buildroot + os.sep + os.path.dirname(env.bouwfile[2:])
        real_target = real_dir + os.sep + target

        # Fill the buildmap
        self.buildmap[full_target] = real_target

        # Make sure the sources have absolute paths
        real_sources = []

        # Find absolute paths of the sources
        for src in sources:
            real_src = os.path.dirname(env.bouwfile) + os.sep + src

            # This source may have a real target in the buildroot
            if real_src in self.buildmap:
                real_sources.append(self.buildmap[real_src])
            else:
                real_sources.append(real_src)

        # Prepare sources string
        real_sources = " ".join(real_sources)

        # Prepare command string
        command = cmd
        command = command.replace("%TARGET%", real_target)
        command = command.replace("%SOURCES%", real_sources)
        command = command.replace("\n", " ")
        command = command.replace("\r", " ")

        # TODO
        print("adding action: " + command)
