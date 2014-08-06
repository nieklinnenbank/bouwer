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

"""
Bouwer action layer

This layer is responsible for executing actions. An action can
be a shell command or a python function. The action layer does not know
about the other layers (build and configuration).
"""

import multiprocessing
import subprocess
import os
import os.path
import sys
import datetime
import logging
import bouwer.util
from bouwer.cli import CommandLine

class Worker(multiprocessing.Process):
    """
    Implements a consumer process for executable :class:`Action` objects.

    The :class:`Worker` class implements a simple consumer for
    executing :class:`Action` objects. It takes a :obj:`dict`
    of available `actions` and receives target names of the
    appropriate action to execute from the `work` :class:`Queue`.
    The worker sends an :class:`ActionEvent` on the `events` :class:`Queue`
    before with type `ActionEvent.EXECUTE` and after executing
    an action with type `ActionEvent.FINISH`.
    """

    def __init__(self, actions, work, events):
        """
        Constructor

        :param dict actions: Dictionary with :class:`Action` objects
        :param :class:`Queue` work: Queue to receive target names to execute
        :param :class:`Queue` events: Queue to publish events to the :class:`WorkerManager`
        """
        super(Worker, self).__init__()
        self._actions = actions
        self._work    = work
        self._events  = events

    def run(self):
        """
        Main execution loop of the Worker. Does not return.
        """
        while True:
            # Retrieve the next Action target
            target = self._work.get()

            # Trigger ActionEvents and execute the action
            self._events.put(ActionEvent(self.name, target, ActionEvent.EXECUTE))
            result = self._actions[target]()
            self._events.put(ActionEvent(self.name, target, ActionEvent.FINISH, result))

class WorkerManager:
    """
    Manages a pool of :class:`Worker` processes
    """

    def __init__(self, actions):
        """
        Constructor

        :param dict actions: Dictionary with :class:`Action` objects
        """
        self.actions  = actions
        self.work     = multiprocessing.Queue()
        self.events   = multiprocessing.Queue()
        self.workers  = []
        self.log      = logging.getLogger(__name__)
        self.output_plugin = getattr(CommandLine.Instance().args, 'output_plugin', None)
        self.running  = []
        self.pending  = self.actions.copy()

        # Create workers
        for i in range(CommandLine.Instance().args.workers):
            worker = Worker(self.actions, self.work, self.events)
            self.workers.append(worker)
            worker.start()

    def __del__(self):
        """
        Destructor
        """
        for proc in self.workers:
            proc.terminate()
            proc.join()

    def execute(self):
        """
        Execute all :class:`.Action` objects
        """
        self.log.debug("running actions")

        while True:
            collecting = True

            # Make as much as possible work available
            while collecting or (self.pending and not self.running):
                collecting = False

                for key in list(self.pending.keys()):
                    action = self.pending[key]
                    if self.decide(action):
                        action.status = ActionEvent.EXECUTE
                        self.work.put(action.target)
                        self.running.append(action)
                        del self.pending[key]
                        collecting = True

            # Wait for events
            if not self.running:
                break

            event  = self.events.get()
            action = self.actions[event.target]
            action.status = event.type
            self.log.debug("event: " + str(event))

            if action.status == ActionEvent.FINISH:
                self.running.remove(action)

            # Report the event to the builder
            action.builder.action_event(action, event)

            # Invoke output plugin.
            if self.output_plugin:
                self.output_plugin.action_event(action, event)

    def decide(self, action):
        """
        Decide if this action needs to run.

        :param :class:`Action` action: the action to try

        Returns `True` if the :class:`Action` needs to run or `False` otherwise.
        """
        need_run = False

        # Is/has the action already ran?
        if action.status is not ActionEvent.CREATE:
            return False

        # Try to see if the target exists
        try:
            my_st = os.stat(action.target)
        except OSError:
            need_run = True

        # Do all our dependencies satisfy?
        for src in action.sources:
            try:
                if self.actions[src].status != ActionEvent.FINISH:
                    return False
            except KeyError:
                pass

            # See if their timestamp is larger than ours
            try:
                st = os.stat(src)
                if not need_run and st.st_mtime > my_st.st_mtime:
                    need_run = True
            except OSError:
                pass

        # Allow override to enfore full build from command line
        if CommandLine.Instance().args.force or need_run:
            return True

        # None of the sources is updated and we exist. Don't build.
        action.status = ActionEvent.FINISH
        del self.pending[action.target]
        return False

class ActionEvent:
    """
    Represents an event which occurred for an :class:`.Action`
    """

    CREATE  = 'create'
    EXECUTE = 'execute'
    FINISH  = 'finish'

    def __init__(self, worker, target, event_type, result = None):
        """
        Constructor

        :param str worker: the name of the :class:`Worker` that caused the event
        :param str target: target of the :class:`Action` for this event
        :param str event_type: type of event
        :param int result: exit code of the :class:`Action`
        """
        self.worker = worker
        self.target = target
        self.type   = event_type
        self.result = result
        self.time   = datetime.datetime.now()

    def __str__(self):
        """
        Convert to string representation
        """
        return 'ActionEvent.' + self.type.upper() + ' : ' + self.target + \
               ' @ worker[' + self.worker + '] type=' + self.type + \
               ' result=' + str(self.result) + ' time=' + str(self.time)

    def __repr__(self):
        """
        Convert to short string representation
        """
        return self.__str__()

class Action:
    """
    Represents an executable action.
    """

    def __init__(self, target, sources, command, tags, builder):
        """
        Constructor

        :param str target: target file for the action
        :param list sources: a `list` of source files as dependency
        :param str command: Either a `str` with a shell command or a python function
        :param dict tags: Dictionary with parameters called tags
        :param :class:`Plugin` builder: the builder that generated this action
        """
        self.target  = target
        self.sources = sources
        self.command = command
        self.tags    = tags
        self.builder = builder
        self.status  = ActionEvent.CREATE

    def __call__(self):
        """
        Execute the action
        """

        # If the command is a python function, run it.
        if callable(self.command):
            return self.command(self)

        # If quiet mode is set, do not show any output
        if 'quiet' in self.tags and self.tags['quiet']: 
            try:
                subprocess.check_output(self.command, stderr=subprocess.PIPE, shell=True)
                return 0
            except subprocess.CalledProcessError as e:
                return e.returncode
        else:
            return os.system(self.command)

    def __str__(self):
        """
        Convert to string representation
        """
        return self.target   + " <<< sources=" + \
           str(self.sources) + " status=" + self.status + " : [" + str(self.command) + "]"

    def __repr__(self):
        """
        Convert to short string representation
        """
        return self.__str__()

class ActionManager(object):
    """
    Manages all :class:`.Action` objects registered for execution.
    """

    def __init__(self):
        """
        Constructor
        """
        self.log     = logging.getLogger(__name__)
        self.actions = {}

    def submit(self, target, sources, command, tags, builder):
        """
        Submit a new :class:`.Action` for execution

        :param str target: target file for the action
        :param list sources: a `list` of source files as dependency
        :param str command: Either a `str` with a shell command or a python function
        :param dict tags: Dictionary with parameters called tags
        :param :class:`Plugin` builder: the builder that generated this action
        """
        if target in self.actions:
            raise Exception("target " + target + " already submitted")

        self.actions[target] = Action(target, sources, command, tags, builder)
        self.log.debug("submitted: " + str(self.actions[target]))

    def run(self, clean = False):
        """
        Run all registered :class:`.Action` objects

        :param bool clean: True to remove the targets. False to execute.
        """

        if clean:
            for action in self.actions.values():
                self.log.debug("removing: " + action.target)
                try:
                    os.remove(action.target)
                except OSError:
                    pass
        else:
            # Allow output plugins
            self.workers = WorkerManager(self.actions)
            self.workers.execute()
            self.workers = None
            self.actions.clear()
