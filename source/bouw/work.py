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

def worker(num, actions, work_queue, done_queue):
    print("Worker " + str(num) + " getting work")

    while True:
        name = work_queue.get()
        print("Worker " + str(num) + " executing: " + actions[name].command)
        os.system(actions[name].command)
        done_queue.put(name)

    print("Worker " + str(num) + " done")

class Master:
    def __init__(self, action_tree):
        self.action_tree = action_tree
        self.num_workers = multiprocessing.cpu_count()
        self.work_queue  = multiprocessing.Queue()
        self.done_queue = multiprocessing.Queue()
        self.workers = []
        pass

    def execute(self):

        # OK, but problem: the queue does NOT wait until the dependencies are compiled 100%
        # Solution: workers must report back when done

        # Fill the queue initially with work not having dependencies
        initial_work = self.action_tree.get_available()
        for work in initial_work:
            self.work_queue.put(work.target)

        # Start workers
        for i in range(self.num_workers):
            p = multiprocessing.Process(target = worker, args = (i, self.action_tree.actions, self.work_queue, self.done_queue, ))
            self.workers.append(p)
            p.start()

#        for dep in self.action_tree.reverse_actions:
#            print("Dependency " + dep + " triggeres: ")
#            for action in self.action_tree.reverse_actions[dep]:
#                print("  " + action.target)

        # Now keep processing until all dependencies are done
        while True:

            work_done = self.done_queue.get()
            print("Done: " + work_done)

            available = self.action_tree.get_available(work_done)
            for action in available:
                print("Available: " + action.target)
                self.work_queue.put(action.target)

            if self.action_tree.is_done():
                print("Nothing available")
                break

        print("We're done!")
        for proc in self.workers:
            proc.terminate()
