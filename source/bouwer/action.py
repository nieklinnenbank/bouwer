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

class Action:

    def __init__(self, target, command, sources, action_map, pretty):
        self.target  = target
        self.command = command
        self.sources = sources
        self.taken   = False
        self.done    = False
        self.action_map = action_map
        self.pretty  = pretty

    def sources_done(self):
        for src in self.sources:
            if src in self.action_map and not self.action_map[src].done:
                return False
        return True

class ActionTree:

    def __init__(self):
        self.buildroot_map = {} # translates the full project path to the
                                # build root path, e.g:
                                #   src/module/foo.o -> build/src/module/foo.o
        self.actions = {}
        self.reverse_actions = {}
        self.num_done = 0

    def get_available(self, command_ready = None):

        ret = []

        # Try to release all actions depending on the completed command
        if command_ready is not None:

            self.actions[command_ready].done = True
            self.num_done = self.num_done + 1

            if command_ready in self.reverse_actions:
                for action in self.reverse_actions[command_ready]:
                    if not action.taken and not action.done and action.sources_done():
                        action.taken = True
                        ret.append(action)

        # Loop the whole actions list for available actions
        else:
            for act in self.actions:
                action = self.actions[act]

                # Only add if all dependencies ready and we're not already processed
                if not action.taken and not action.done and action.sources_done():
                    action.taken = True
                    ret.append(action)

        return ret

    def is_done(self):
        return self.num_done == len(self.actions)

    def add(self, target, cmd, sources, env, pretty):

        # Honour the buildroot setting
        buildroot = env['buildroot'] + os.sep + env['id']

        # Full path to the target from the top-level Bouwfile
        full_target = os.path.dirname(env.bouwfile) + os.sep + target

        # Real path to the target, using a buildroot
        real_dir    = buildroot + os.sep + os.path.dirname(env.bouwfile[2:])
        real_target = real_dir + os.sep + target

        # Fill the buildmap
        self.buildroot_map[full_target] = real_target

        # Make sure the sources have absolute paths
        real_sources = []

        # Find absolute paths of the sources
        for src in sources:
            real_src = os.path.dirname(env.bouwfile) + os.sep + src

            # This source may have a real target in the buildroot
            if real_src in self.buildroot_map:
                real_sources.append(self.buildroot_map[real_src])
            else:
                real_sources.append(real_src)

        # Prepare command string
        command = cmd
        command = command.replace("%TARGET%", real_target)
        command = command.replace("%SOURCES%", " ".join(real_sources))
        command = command.replace("\n", " ")
        command = command.replace("\r", " ")

        # Make target directory, if not existing
        if not os.path.exists(os.path.dirname(real_target)):
            os.makedirs(os.path.dirname(real_target))

        # Add the action
        action = Action(real_target, command, real_sources, self.actions, pretty)

        self.actions[real_target] = action

        for dep in action.sources:
            if not dep in self.reverse_actions:
                self.reverse_actions[dep] = []
            self.reverse_actions[dep].append(action)
