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
import sys
import argparse
from bouwer.plugin import *

##
# Configure using standard I/O
#
class LineConfig(Plugin):

    ##
    # Initialize plugin
    #
    def initialize(self, conf):

        conf.cli.parser.add_argument('--lineconfig',
            dest    ='config_plugin',
            action  ='store_const',
            const   = self,
            default = argparse.SUPPRESS,
            help    = 'Change configuration using standard I/O interface')

    ##
    # Main configuration routine
    #
    def configure(self, conf):

        self.item_count  = 0

        # TODO: put this in the global config module
        self.item_total  = len(conf.items)
        self.item_total += len(conf.trees)

        for tree in conf.trees:
            self.item_total += len(conf.trees[tree].items)

        for path in conf.path_map:
            print()
            print(str(os.path.relpath(path)))

            for obj in conf.path_map[path]:

                # Increase item count
                self.item_count += 1

                while self._change_item(obj) is not True: pass

        # TODO: prompt first here!
        conf.save()
        print('Configuration saved!')

    ##
    # Change a configuration item
    #
    def _change_item(self, item):

        # Print the prompt for this item
        self._print_prompt(item)

        # Read the user input
        try:
            line = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            print()
            sys.exit(1)

        # No input means keep the current value
        if len(line) == 0: return True

        # Question mark means print the help
        if line == '?':
            print(item.keywords['help'])
            return False

        # Change a boolean
        if item.type == bool:
            if line == 'Y' or line == 'y': item.value = True
            if line == 'N' or line == 'n': item.value = False
            if line == 'k': pass
            if line == '?': pass

        # Change a string
        if item.type == str:
            item.value = line

        # Change a list
        if item.type == list:
            try:
                item.value = item.keywords['default'][int(line) - 1]
            except ValueError as e:
                return False

        # Success
        return True

    ##
    # Print the prompt for changing the given item.
    #
    def _print_prompt(self, item):

        prompt = '{' + str(self.item_count) + '/' + str(self.item_total) + '} '

        if 'title' in item.keywords:
            prompt += item.keywords['title']
        else:
            prompt += item.name

        if item.type == list:
            prompt += ' [' + str(item.value) + '] '
            print(prompt)

            n = 1
            for item in item.keywords['default']:
                print('\t(' + str(n) + ') : ' + item.keywords['title'])
                n += 1

            prompt = '\t(1-' + str(n - 1) + '/k/?) '
            print(prompt, end = '')
            sys.stdout.flush()

        else:
            if item.type == bool:  prompt += ' (Y/y/N/n/k/?) '
            if item.type == str:   prompt += ' (str/k/?) '
            if item.type == int:   prompt += ' (int/k/?) '
            if item.type == float: prompt += ' (float/k/?) '

            prompt += ' [' + str(item.value) + '] '
            print(prompt, end = '')
            sys.stdout.flush()
