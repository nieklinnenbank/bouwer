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

class Worker(multiprocessing.Process):
    """
    Implements a consumer process for executable actions

    The :class:`Worker` class implements a simple consumer for
    executing :class:`Action` objects. It takes a :obj:`list`
    of available `actions` and receives target names of the
    appropriate action to execute from the `work` :class:`Queue`.
    The worker sends an :class:`ActionEvent` on the `events` :class:`Queue`
    before and after executing an action.
    """

    def __init__(self, actions, work, events):
        """
        Constructor
        """
        super().__init__()
        self._actions = actions
        self._work    = work
        self._events  = events

    def run(self):
        """
        Main execution loop of the Worker.
        """
        while True:
            # Retrieve the next Action target
            target = self._work.get()

            # Trigger ActionEvents and execute the action
            self._events.put(ActionEvent(self.name, target, 'execute'))
            result = self._actions[target]()
            self._events.put(ActionEvent(self.name, target, 'finish', result))

class WorkerManager:
    """
    Manages a pool of :class:`Worker` processes
    """

    def __init__(self, actions, num_workers, plugins):
        """
        Constructor
        """
        self._workers = []
        self._work    = multiprocessing.Queue()
        self._events  = multiprocessing.Queue()
        self.log      = logging.getLogger(__name__)

        # Create workers
        for i in range(num_workers):
            worker = Worker(actions, self._work, self._events)
            self._workers.append(worker)
            worker.start()

    def __del__(self):
        """
        Destructor
        """
        for proc in self._workers:
            proc.terminate()

    def execute(self, collect, finished, handle_event):
        """
        Execute the given :obj:`list` of actions
        """
        self.log.debug("executing actions")

        # Fill the work queue initially with work
        for work in collect():
            self._work.put(work.target)

        # Now keep processing until all dependencies are done
        while True:
            
            if finished() and self._work.empty():
                break

            self.log.debug("waiting for event")
            ev = self._events.get()
            self.log.debug("got event: " + str(ev))
            
            if ev.event == 'finish':
                if ev.result != 0:
                    break

                self.log.debug("finished " + str(ev.target) + " by " + str(ev.worker))
            
                for action in collect(ev.target):
                    self.log.debug("sending " + str(action))
                    self._work.put(action.target)
            
            # Let our caller post process the event
            handle_event(ev)

        # TODO: possible to output stats, e.g. number of actions per worker, etc
        #       this should be part of an output plugin too?
        # TODO: output a completed ActionEvent here
        self.log.debug("completed")
 
class ActionEvent:
    """
    Represents an event which occurred for an action.
    """

    def __init__(self, worker, target, event, result = None):
        """
        Constructor
        """ 
        self.worker = worker
        self.target = target
        self.event  = event
        self.result = result
        self.time   = datetime.datetime.now()

class Action:
    """
    Represents an executable action.
    """

    def __init__(self, args, target, sources, command):
        """
        Constructor
        """
        self.args    = args
        self.target  = target
        self.sources = sources
        self.command = command
        self.provide = []

    def satisfied(self, pending, running):
        """
        See if our dependencies are satisfied.
        
        >>> action.satisfied(pending, running)
        True
        """
        for src in self.sources:
            if src in pending or src in running:
                return False
        return True

    def decide(self, pending, running):
        """
        Decide if this action needs to run.
       
        >>> action.decide(pending, running)
            True
        """

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

    def __call__(self):
        """
        Execute the action
        """
        return os.system(self.command)

    def __str__(self):
        """
        Convert to string representation
        """
        return self.target   + " <<< sources=" + \
           str(self.sources) + " provide=" + \
           str(self.provide) + "  :  [" + \
           str(self.command) + "]"

    def __repr__(self):
        """
        Convert to short string representation
        """
        return self.target

class ActionManager:
    """
    Represents all actions registered for execution.
    """

    def __init__(self, args, plugins):
        """
        Constructor
        """
        self.args = args
        self.plugins = plugins
        self.log  = logging.getLogger(__name__)
        # TODO: replace with invoke()
        self._output_plugin = plugins.output_plugin()
        self.clear()

    def clear(self):
        """
        Remove all submitted actions.
        """

        # TODO: don't do this with lists?
        self.pending  = {}
        self.running  = {}
        self.finished = {}
        self.work     = multiprocessing.Queue()
        self.events   = multiprocessing.Queue()
        self.workers  = []

    def submit(self, target, sources, command):
        """
        Submit a new :class:`.Action` for execution
        
        >>> manager.submit('hello', ['hello.c'], 'gcc -o hello hello.c')
        """ 
        if target in self.pending:
            raise Exception("target " + str(target) + " already submitted")

        action = Action(self.args, target, sources, command)
        self.pending[target] = action

        # TODO: circular dep check
        for src in sources:
            if src in self.pending:
                self.pending[src].provide.append(target)

        self.log.debug("submitted action " + str(action))

    def run(self):
        """
        Run all registered actions
        """
        master = WorkerManager(self.pending, self.args.workers, self.plugins)
        master.execute(self.collect, self._done, self._event)

    def _event(self, ev):
        """
        Process an ActionEvent by invoking output plugins
        """

        # TODO: use class constants instead of strings
        # TODO: pass the action manager instead?
        #       together with the current configuration
        if ev.event == 'execute':
            self._output_plugin.output(self.running[ev.target],
                                       ev,
                                       pending=len(self.pending),
                                       running=len(self.running),
                                       finished=len(self.finished))
            
        elif ev.event == 'finish':
            self._output_plugin.output(self.finished[ev.target],
                                       ev,
                                       pending=len(self.pending),
                                       running=len(self.running),
                                       finished=len(self.finished))
 
    def collect(self, target = None):
        """
        Retrieve more actions to execute
        """
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

    def _finish(self, target):
        """
        Post-process an action after completion.
        """
        action = self.running.pop(target)
        self.finished[target] = action

        # TODO: release all reverse dependencies now
        ret = []

        # TODO: cleanup this bit please..
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

    def _done(self):
        """
        Check if all actions are done
        """
        return len(self.pending) == 0 and len(self.running) == 0
        
    def dump(self):
        """
        Dump internal information to standard output
        """
        self.log.debug("pending  = " + str(self.pending.keys()))
        self.log.debug("running  = " + str(self.running.keys()))
        self.log.debug("finished = " + str(self.finished.keys()))

