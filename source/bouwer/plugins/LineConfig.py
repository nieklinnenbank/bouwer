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

    def initialize(self):
        """ Initialize plugin """
        self.conf.cli.parser.add_argument('--lineconfig',
            dest    = 'config_plugin',
            action  = 'store_const',
            const   = self,
            default = argparse.SUPPRESS,
            help    = 'Change configuration using standard I/O interface')

    ##
    # Main configuration routine
    #
    def configure(self, conf):

        self.item_count = 0
        self.item_total = len(conf.trees)
        self.done       = []

        for tree_name, tree in conf.trees.items():
            self.item_total += len(tree.subitems)

        for tree_name, tree in conf.trees.items():
            for path in sorted(tree.bouwconfigs):
                self.print_path = False

                for item in tree.bouwconfigs[path]:
                    self._change_item(conf, tree, path, item)

        # Ask to save the modified configuration.
        print()
        sys.stdout.write('Save Configuration? (y/n) [n] ')
        sys.stdout.flush()

        try:
            if sys.stdin.readline().strip().lower() == 'y':
                conf.save()
                print('Configuration saved!')
                print()                
                conf.dump()
        except KeyboardInterrupt:
            print()
            return 1
        return 0

    ##
    # Attempt to change a configuration item
    #
    def _change_item(self, conf, tree, path, item):
    
        # First ask for our dependencies, if needed
        for dep in item.keywords.get('depends', []):
            if dep in tree.subitems:
                self._change_item(conf, tree, path, tree.subitems[dep])

        # If this item is not satisfied in this tree, skip it
        if not item.satisfied(tree):
            return

        # If item already done, don't bother again
        if item in self.done:
            return

        # Ask the user for the item value, if not only selectable list item.
        # TODO: broken!!! GCC isn't asked anymore for TARGET and HOST...
        if item.keywords.get('in_list', None) is None:
            while self._try_change_item(conf, tree, path, item) is not True:
                pass

        # Otherwise, just print the item type and title for asking keywords?
        # TODO: if no keywords available, this is useless..
        else:
            self._print_prompt(tree, path, item, False)
            print()
        
        # Ask the user for the item keywords.
        for key in item.keywords:
            while self._try_change_keyword(conf, tree, item, key) is not True:
                pass
        
        # Append to done list
        self.done.append(item)

        # For a list, also mark all options done
        if item.type == list:
            for opt in item.keywords.get('default', []):
                self.done.append(tree.subitems[opt])

    def _read_input(self):

        # Read the user input
        try:
            return sys.stdin.readline().strip()
        except KeyboardInterrupt:
            print()
            sys.exit(1)


    ##
    # Change a configuration item
    #
    def _try_change_item(self, conf, tree, path, item):

        # Print the prompt for this item
        self._print_prompt(tree, path, item)
        
        # Read input from user
        line = self._read_input()

        # No input means keep the current value
        if len(line) == 0: return True

        # Question mark means print the help
        if line == '?':
            print(item.keywords.get('help', 'No help available'))
            return False

        # Change a boolean
        if item.type == bool:
            if line == 'Y' or line == 'y': item.update(True)
            if line == 'N' or line == 'n': item.update(False)
            if line == 'k': pass
            if line == '?': pass

        # Change a string
        if item.type == str: item.update(line)

        # Change an integer
        if item.type == int: item.update(int(line))
        
        # Change a float
        if item.type == float: item.update(float(line))

        # Change a list
        if item.type == list:
            try:
                item.update(item.keywords['default'][int(line) - 1])
                
                # TODO: ask for the selected item's keywords too
                
            except ValueError as e:
                return False

        # Success
        return True

    ##
    # Change a configuration keyword
    #
    def _try_change_keyword(self, conf, tree, item, key):
    
        # Ignore special keywords
        if key in ['title', 'help', 'default', 'childs', 'depends', 'in_list', 'tree']:
            return True
    
        sys.stdout.write('  [key]   ' + key + ' [' + str(item.keywords[key]) + '] ')
        sys.stdout.flush()
        line = self._read_input()
        return True

    ##
    # Print the input prompt for changing the given item.
    #
    def _print_prompt(self, tree, path, item, input = True):

        # Do we first need to print the Bouwconfig path?
        if not self.print_path:
            print()
            print(tree.name + ' : ' + str(os.path.dirname(os.path.relpath(path))))
            self.print_path = True

        title = item.keywords.get('title', item.name)

        if item.type == list:
            print('[list]  ' + title +' [' + str(item.value(tree)) + '] ')

            n = 1
            for item_name in item.keywords['default']:
                subitem = tree.subitems[item_name]
                print('\t(' + str(n) + ') : ' + subitem.keywords.get('title', subitem.name))
                n += 1

            if input:
                sys.stdout.write('\t(1-' + str(n - 1) + '/?) ')
            sys.stdout.flush()

        else:
            if item.type == bool:
                prompt = '[bool]  ' + title
                if input: prompt += ' (Y/y/N/n/?) '

            if item.type == str:
                prompt = '[str]   ' + title
                if input: prompt += ' (str/?) '

            if item.type == int:
                prompt = '[int]   ' + title
                if input: prompt += ' (int/?) '
                
            if item.type == float:
                prompt = '[float] ' + title
                if input: prompt += ' (float/?) '

            if input:
                prompt += ' [' + str(item.value(tree)) + '] '

            sys.stdout.write(prompt)
            sys.stdout.flush()

