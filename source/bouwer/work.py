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

##
# Function executed by the worker processes
#
# @param num ID number of the worker
# @param actions Reference to the actions tree
# @param work_queue Reference to the worker queue
# @param done_queue Reference to the done queue
#
def worker(num, actions, work_queue, done_queue):

    while True:
        name = work_queue.get()

        if actions[name].pretty is not None:
            print("[" + str(num) + "]  " + actions[name].pretty + "  " + actions[name].target)
        else:
            print("[" + str(num) + "] ==> " + actions[name].command)
        os.system(actions[name].command)
        done_queue.put(name)

class Master:

    ##
    # Constructor
    #
    def __init__(self, action_tree, config, args):
        self.action_tree = action_tree
        self.config = config
        self.args   = args
        self.num_workers = multiprocessing.cpu_count()
        self.work_queue  = multiprocessing.Queue()
        self.done_queue = multiprocessing.Queue()
        self.workers = []
        pass

    def execute(self):

        # Fill the queue initially with work not having dependencies
        initial_work = self.action_tree.get_available()
        for work in initial_work:
            self.work_queue.put(work.target)

        # Start workers
        for i in range(self.num_workers):
            p = multiprocessing.Process(target = worker, args = (i, self.action_tree.actions, self.work_queue, self.done_queue, ))
            self.workers.append(p)
            p.start()

        # Now keep processing until all dependencies are done
        while not self.action_tree.is_done():
            work_done = self.done_queue.get()

            available = self.action_tree.get_available(work_done)
            for action in available:
                self.work_queue.put(action.target)

        for proc in self.workers:
            proc.terminate()
