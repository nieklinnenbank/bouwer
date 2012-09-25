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

import multiprocessing
import queue
import os
import os.path
import sys
import datetime
import logging

##
# Implements a worker for executing Actions.
#
class Worker(multiprocessing.Process):

    ##
    # Constructor
    #
    # @param actions Reference to the ActionManager
    # @param work Reference to the work queue
    # @param events Reference to the events queue
    #
    def __init__(self, actions, work, events):
        super().__init__()
        self.actions = actions
        self.work    = work
        self.events  = events

    ##
    # Main execution loop of the worker.
    #
    def run(self):

        while True:
            # Retrieve the next Action target
            target = self.work.get()
            
            # Trigger ActionEvents and execute the action
            self.events.put(ActionEvent(self.name, target, 'execute'))
            result = self.actions[target]()
            self.events.put(ActionEvent(self.name, target, 'finish', result))

##
# Represents an event which occurred for an Action.
#
class ActionEvent:

    ##
    # Constructor
    #
    # @param worker Name of the worker causing the event
    # @param target Target of the action
    # @param event String describing the event that occurred
    # @param result Optional result code of the event
    #
    def __init__(self, worker, target, event, result = None):
        self.worker = worker
        self.target = target
        self.event  = event
        self.result = result
        self.time   = datetime.datetime.now()

##
# This class contains a single action to be executed.
#
class Action:

    ##
    # Constructor
    #
    def __init__(self, args, target, sources, command):
        self.args    = args
        self.target  = target
        self.sources = sources
        self.command = command
        self.provide = []

    ##
    # See if our dependencies are done.
    #
    # @param pending list of pending actions
    # @param running list of running actions
    #
    def satisfied(self, pending, running):
        for src in self.sources:
            if src in pending or src in running:
                return False
        return True

    ##
    # Decide if this action needs to run.
    #
    def decide(self, pending, running):

        # Try to see if the target exists
        try:
            my_st = os.stat(self.target)
        except OSError:
            return True

        # See if any of the sources changed.
        for src in self.sources:
            
            # If the source to-be-completed, we always build.
            if src in pending or src in running:
                return True

            # See if their timestamp is larger than ours
            st = os.stat(src)
            if st.st_mtime > my_st.st_mtime:
                return True

        # TODO: also decide() against the .bouwconf / Configuration!
        # Since, we need to (partly) rebuild if the config has changed.
                    
        # None of the sources is updated and we exist. Don't build.
        return self.args.force

    ##
    # Execute the Action
    #
    def __call__(self):
        return os.system(self.command)

    ##
    # Convert action to string representation.
    #
    def __str__(self):
        return self.target   + " <<< sources=" + \
           str(self.sources) + " provide=" + \
           str(self.provide) + "  :  [" + \
           str(self.command) + "]"

    ##
    # Convert to short string representation.
    #
    def __repr__(self):
        return self.target

##
# Represents all Actions registered for execution.
#
class ActionManager:

    ##
    # Constructor
    #
    # @param args command line arguments
    # @param plugins Access to the plugin layer.
    #
    def __init__(self, args, plugins):
        self.args = args
        self.log  = logging.getLogger(__name__)
        self.output_plugin = plugins.output_plugin()
        self.num_workers   = args.workers
        self.clear()

    ##
    # Remove all submitted actions.
    #
    def clear(self):
        self.pending  = {}
        self.running  = {}
        self.finished = {}
        self.work     = multiprocessing.Queue()
        self.events   = multiprocessing.Queue()
        self.workers  = []

    ##
    # Put a new Action on the ActionTree.
    #
    # @param target Name of the output file or None
    # @param sources List of dependencies
    # @param command Command to execute or a python function
    #
    def submit(self, target, sources, command):

        if target in self.pending:
            raise Exception("target " + str(target) + " already submitted")

        action = Action(self.args, target, sources, command)
        self.pending[target] = action

        # TODO: circular dep check
        for src in sources:
            if src in self.pending:
                self.pending[src].provide.append(target)

        self.log.debug("submitted action " + str(action))

    ##
    # Run all submitted actions.
    #
    def run(self):
        
        self.log.debug("running actions")

        # Create workers
        for i in range(self.num_workers):
            w = Worker(self.pending, self.work, self.events)
            self.workers.append(w)
            w.start()

        # Fill the queue initially with work not having dependencies
        for work in self._collect():
            self.work.put(work.target)

        # Now keep processing until all dependencies are done
        while not self._done():
            self.log.debug("waiting for event")

            ev = self.events.get()

            if ev.event == 'execute':
                self.output_plugin.output(self.running[ev.target],
                                          ev,
                                          pending=len(self.pending),
                                          running=len(self.running),
                                          finished=len(self.finished))
            
            elif ev.event == 'finish':
                if ev.result != 0:
                    break

                self.log.debug("finished " + str(ev.target) + " by " + str(ev.worker))
                
                self.output_plugin.output(self.running[ev.target],
                                          ev,
                                          pending=len(self.pending),
                                          running=len(self.running) - 1,
                                          finished=len(self.finished) + 1)
            
                for action in self._collect(ev.target):
                    self.log.debug("sending " + str(action))
                    self.work.put(action.target)
            
        self.log.debug("completed")

        # Stop all workers
        # TODO: possible to output stats, e.g. number of actions per worker, etc
        #       this should be part of an output plugin too?
        for proc in self.workers:
            proc.terminate()

    ##
    # Retrieve the next available Action for execution.
    #
    # @param target Optional completed action or None.
    # @return List of Actions for execution.
    #
    def _collect(self, target = None):

        if target is None:
            runnable = []
        else:
            runnable = self._finish(target)
        
        for name in list(self.pending.keys()):

            if name not in self.pending:
                continue

            work = self.pending[name]

            if work.satisfied(self.pending, self.running):

                self.log.debug("satisfied with " + str(work))

                self.running[name] = work
                del self.pending[name]

                if work.decide(self.pending, self.running):
                    runnable.append(work)
                else:
                    runnable = runnable + self._finish(name)

        self.log.debug("runnable is " + str(runnable))
        return runnable

    ##
    # Called when an action is completed.
    #
    # @param target Target of the action which just completed
    #
    def _finish(self, target):
        action = self.running.pop(target)
        self.finished[target] = action

        # TODO: release all reverse dependencies now
        ret = []
        
        for name in action.provide:
            if name in self.pending:
                act = self.pending.get(name)
                
                self.log.debug("trying to release providing " + str(act))
                
                if act.satisfied(self.pending, self.running):
                    del self.pending[name]
                    self.log.debug("satisfied with providing " + str(act))
                    
                    if act.decide(self.pending, self.running):
                        self.log.debug("running providing " + str(act))
                        
                        self.running[name] = act
                        ret.append(act)
                    else:
                        self.log.debug("finising providing " + str(act))
                        self.finished[name] = act
        
        return ret

    ##
    # See if all Actions are done.
    #
    # @return True if finished, False otherwise.
    #
    def _done(self):
        return len(self.pending) == 0 and len(self.running) == 0
        
    ##
    # Dump all our information to stdout for diagnosis.
    #
    def dump(self):
        self.log.debug("pending  = " + str(self.pending.keys()))
        self.log.debug("running  = " + str(self.running.keys()))
        self.log.debug("finished = " + str(self.finished.keys()))
