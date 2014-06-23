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
from bouwer.config import *

class LineConfig(Plugin):
    """
    Configure using standard input
    """

    def initialize(self):
        """
        Initialize plugin
        """
        self.conf.cli.parser.add_argument('--lineconfig',
            dest    = 'config_plugin',
            action  = 'store_const',
            const   = self,
            default = argparse.SUPPRESS,
            help    = 'Change configuration using standard I/O interface')

    def configure(self, conf):
        """
        Main configuration routine
        """

        self.done = []

        # Loop all bouwconfig in order
        for tree_name, tree in conf.trees.items():
            for bouwconf in conf.bouwconf_map:
                self.print_path = False

                for item in conf.bouwconf_map[bouwconf]:
                    self._change_item(conf, tree, bouwconf, item)

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

    def _change_item(self, conf, tree, path, item):
        """
        Attempt to change a configuration item
        """

        # First ask for our dependencies, if needed
        for dep in item._keywords.get('depends', []):
            if dep in tree.subitems:
                for dep_path in tree.subitems[dep]:
                    self._change_item(conf, tree, dep_path, tree.subitems[dep][dep_path])

        # If this item is not satisfied in this tree, skip it
        if not item.satisfied(tree):
            return

        # If item already done, don't bother again
        if item in self.done:
            return

        # Ask the user for the item value, if not only selectable list item.
        # TODO: broken!!! GCC isn't asked anymore for TARGET and HOST...
        if item._keywords.get('in_list', None) is None:
            while self._try_change_item(conf, tree, path, item) is not True:
                pass

        # Otherwise, just print the item type and title for asking keywords?
        # TODO: if no keywords available, this is useless..
        else:
            self._print_prompt(tree, path, item, False)
            print()
        
        # Ask the user for the item keywords.
        for key in item._keywords:
            while self._try_change_keyword(conf, tree, item, key) is not True:
                pass
        
        # Append to done list
        self.done.append(item)

        # For a list, also mark all options done
        if type(item) == ConfigList:
            for opt in item._keywords.get('options', []):
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
            print(item._keywords.get('help', 'No help available'))
            return False

        # Change a boolean
        if type(item) is ConfigBool:
            if line == 'Y' or line == 'y': item.update(True)
            if line == 'N' or line == 'n': item.update(False)
            if line == 'k': pass
            if line == '?': pass

        # Change a string
        if type(item) is ConfigString: item.update(line)

        # Change an integer
        if type(item) is ConfigInt: item.update(int(line))
        
        # Change a float
        if type(item) is ConfigFloat: item.update(float(line))

        # Change a list
        if type(item) is ConfigList:
            try:
                item.update(item._keywords['options'][int(line) - 1])
                
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
        if key in ['title', 'help', 'options', 'depends', 'in_list', 'tree']:
            return True
    
        sys.stdout.write('  [key]   ' + key + ' [' + str(item._keywords[key]) + '] ')
        sys.stdout.flush()
        line = self._read_input()
        if line:
            item._keywords[key] = line

        return True

    def _print_prompt(self, tree, path, item, input = True):
        """ 
        Print the input prompt for changing the given item.
        """

        # Do we first need to print the Bouwconfig path?
        if not self.print_path:
            print
            print(tree.name + ' : ' + path)
            self.print_path = True

        title = item._keywords.get('title', item.name)

        if type(item) is ConfigList:
            print('[list]  ' + title +' [' + str(item.value(tree)) + '] ')

            n = 1
            for item_name in item._keywords['options']:
                subitem = tree.get(item_name)
                print('\t(' + str(n) + ') : ' + subitem._keywords.get('title', subitem.name))
                n += 1

            if input:
                sys.stdout.write('\t(1-' + str(n - 1) + '/?) ')
            sys.stdout.flush()

        else:
            if type(item) is ConfigBool:
                prompt = '[bool]  ' + title
                if input: prompt += ' (Y/y/N/n/?) '

            if type(item) is ConfigString:
                prompt = '[str]   ' + title
                if input: prompt += ' (str/?) '

            if type(item) is ConfigInt:
                prompt = '[int]   ' + title
                if input: prompt += ' (int/?) '
                
            if type(item) is ConfigFloat:
                prompt = '[float] ' + title
                if input: prompt += ' (float/?) '

            if input:
                prompt += ' [' + str(item.value(tree)) + '] '

            sys.stdout.write(prompt)
            sys.stdout.flush()

