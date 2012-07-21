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

    ##
    # Constructor
    #
    def __init__(self, target, command, sources, action_map, pretty):
        self.target  = target
        self.command = command
        self.sources = sources
        self.taken   = False
        self.done    = False
        self.action_map = action_map
        self.pretty  = pretty

    ##
    # Decide if this Action needs execution, based on the sources timestamps.
    #
    def decide_execution(self):
        try:
            my_st = os.stat(self.target)
            num_done = 0

            for src in self.sources:

                # If the source is not marked done, we must always build
                if src in self.action_map and not self.action_map[src].done:
                    break

                # See if the timestamp is larger than ours
                st = os.stat(src)
                if st.st_mtime <= my_st.st_mtime:
                    num_done = num_done + 1

            if num_done >= len(self.sources):
                self.done = True
                self.taken = True

        except OSError:
            pass

    def sources_done(self):
        for src in self.sources:
            if src in self.action_map and not self.action_map[src].done:
                return False
        return True

    ##
    # Execute only when not already (being) executed and dependencies done.
    #
    def can_execute(self):
        return not self.taken and not self.done and self.sources_done()

##
# Represents all Actions registered for execution.
#
class ActionTree:

    ##
    # Constructor
    #
    def __init__(self):
        self.buildroot_map = {} # translates the full project path to the
                                # build root path, e.g:
                                #   src/module/foo.o -> build/src/module/foo.o
        self.actions = {}
        self.reverse_actions = {}
        self.num_done = 0
        self.num_needed = 0

    def get_available(self, command_ready = None):

        ret = []

        # Try to release all actions depending on the completed command
        if command_ready is not None:

            self.actions[command_ready].done = True
            self.num_done = self.num_done + 1

            if command_ready in self.reverse_actions:
                for action in self.reverse_actions[command_ready]:
                    if action.can_execute():
                        action.taken = True
                        ret.append(action)

        # Loop the whole actions list for available actions
        else:
            for act in self.actions:
                action = self.actions[act]

                # Only add if all dependencies ready and we're not already processed
                if action.can_execute():
                    action.taken = True
                    ret.append(action)

        return ret

    ##
    # Check whether all Actions are executed.
    #
    def is_done(self):
        return self.num_done == self.num_needed

    ##
    # Put a new Action on the ActionTree.
    #
    def add(self, target, cmd, sources, env, pretty):

        # Prepare command string
        command = cmd
        command = command.replace("%TARGET%", target)
        command = command.replace("%SOURCES%", " ".join(sources))
        command = command.replace("\n", " ")
        command = command.replace("\r", " ")

        # Make target directory, if not existing
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))

        # Add the action
        action = Action(target, command, sources, self.actions, pretty)

        # If not forced, decide on avoiding this Action
        if not env.args.force:
            action.decide_execution()

        # Increment num_needed
        if not action.done:
            self.num_needed = self.num_needed + 1

        # Add to the target -> action map
        self.actions[target] = action

        # Add to the dependency -> action map
        for dep in action.sources:
            if not dep in self.reverse_actions:
                self.reverse_actions[dep] = []
            self.reverse_actions[dep].append(action)
