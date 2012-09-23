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

##
# Function executed by the worker processes
#
# @param num ID number of the worker
# @param actions Reference to the ActionManager
# @param work_queue Reference to the worker queue
# @param done_queue Reference to the done queue
# @param output_plugin Output function
#
def worker(num, actions, work_queue, done_queue, output_plugin):

    while True:
        name = work_queue.get()

        output_plugin.output(actions[name], stage='running', worker=num)

        result = os.system(actions[name].command)

        done_queue.put((num, name, result))

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
        self.args    = args
        self.output_plugin = plugins.output_plugin()
        # TODO: this must be configurable using args
        self.num_workers = args.workers #multiprocessing.cpu_count()
        self.clear()

    ##
    # Remove all submitted actions.
    #
    def clear(self):
        self.pending    = {}
        self.running    = {}
        self.finished   = {}
        self.work_queue = multiprocessing.Queue()
        self.done_queue = multiprocessing.Queue()
        self.workers    = []

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
        
        if self.args.verbose:
            print("ActionManager: submitted action: " + str(action))

    ##
    # Run all submitted actions.
    #
    def run(self):

        if self.args.verbose:
            print("ActionManager: running actions")

        # Create workers
        for i in range(self.num_workers):
            p = multiprocessing.Process(target = worker,
                                        args = (i, self.pending,
                                                   self.work_queue,
                                                   self.done_queue,
                                                   self.output_plugin,))
            p.start()
            self.workers.append(p)

        # Fill the queue initially with work not having dependencies
        for work in self._collect():
            self.work_queue.put(work.target)

        # Now keep processing until all dependencies are done
        while not self._done():
            if self.args.verbose:
                print("ActionManager: waiting for results")
            num, work_done, result = self.done_queue.get()

            if result != 0:
                break
            
            if self.args.verbose:
                print("ActionManager: finished " + str(work_done) + " by " + str(num))

            self.output_plugin.output(self.running[work_done],
                                      stage='finished',
                                      pending=len(self.pending),
                                      running=len(self.running) - 1,
                                      finished=len(self.finished) + 1)

            for action in self._collect(work_done):
                if self.args.verbose:
                    print("ActionManager: running " + str(action))
                self.work_queue.put(action.target)

        if self.args.verbose:
            print("ActionManager: completed")

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

                if self.args.verbose:
                    print("ActionManager: satisfied with " + str(work))

                self.running[name] = work
                del self.pending[name]

                if work.decide(self.pending, self.running):
                    runnable.append(work)
                else:
                    runnable = runnable + self._finish(name)

        if self.args.verbose:
            print("ActionManager: runnable = " + str(runnable))
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
                
                if self.args.verbose:
                    print("ActionManager: trying to release providing " + str(act))
                
                if act.satisfied(self.pending, self.running):
                    del self.pending[name]
                    if self.args.verbose: print("ActionManager: satisfied with providing " + str(act))
                    
                    if act.decide(self.pending, self.running):
                        if self.args.verbose: print("ActionManager: running providing " + str(act))
                        
                        self.running[name] = act
                        ret.append(act)
                    else:
                        if self.args.verbose: print("ActionManager: finising providing " + str(act))
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

        print("--- Actions Pending ---")
        print()
        for name, action in self.pending.items():
            print(str(action))
        print()

        print("--- Actions Running ---")
        print()
        for name, action in self.running.items():
            print(str(action))
        print()
        
        print("--- Actions Finished ---")
        print()
        for name, action in self.finished.items():
            print(str(action))
        print()
