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
        conf.cli.parser.add_argument('--lineconfig', dest='config_plugin',
            action='store_const', const=self, default=argparse.SUPPRESS,
            help='Change configuration using standard I/O interface')

    ##
    # Main configuration routine
    #
    def configure(self, conf):

        self.item_count  = 0
        self.item_total  = len(conf.items)
        self.item_total += len(conf.trees)

        for item in conf.items:
            self._prompt_change(conf.items[item])

#        for tree in conf.trees:
#            for item in tree.items:
#                self._prompt_change(item)

        conf.save()
        print('Configuration saved!')

    def _prompt_change(self, item):

        prompt = '{' + str(self.item_count) + '/' + str(self.item_total) + '} '

        self.item_count += 1

        if 'title' in item.keywords:
            prompt += item.keywords['title']
        else:
            prompt += item.name

        # Please change this intelligently for various types of config items plz.
        # e.g. for boolean items, this is true, but for strings, it's not.
        prompt += ' (Y/y/N/n/?) '

        if 'default' in item.keywords:
            prompt += ' [' + str(item.keywords['default']) + ']'

        print(prompt)
