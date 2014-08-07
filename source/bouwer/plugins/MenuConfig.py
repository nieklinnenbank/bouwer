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
from bouwer.plugin import Plugin

class MenuConfig(Plugin):
    """
    Configure using the urwid / ncurses text-console frontend
    """

    def initialize(self):
        """
        Initialize the plugin
        """
        self.conf.cli.parser.add_argument('--menuconfig', dest='config_plugin',
            action='store_const', const=self, default=argparse.SUPPRESS,
            help='Change configuration using text console interface (urwid)')

    def configure(self, conf):
        """
        Configure using urwid
        """
        try:
            import urwid
        except:
            sys.exit('urwid python module not installed')

        palette = [
            ('banner', 'black', 'light gray'),
            ('streak', 'black', 'dark red'),
            ('bg', 'black', 'dark blue'),]

        def show_or_exit(key):
            if key in ('q', 'Q'):
                raise urwid.ExitMainLoop()

        tree_checkboxes=[]
        tree_checkboxes.append(urwid.Divider())
        tree_checkboxes.append(urwid.Divider())
        tree_checkboxes.append(urwid.Divider("=", 1))
        for tree in conf.trees.values():
            tree_checkboxes.append(urwid.CheckBox(tree.name, tree.value(tree)))

        lst = urwid.ListBox(urwid.SimpleListWalker(tree_checkboxes))

        # Frame
        w = urwid.Filler(lst, height=('relative', 100), valign='middle')
        w = urwid.AttrWrap(lst, 'body')
        w = urwid.AttrWrap(w, 'bg')
        hdr = urwid.Text("Urwid BigText example program - F8 exits.")
        hdr = urwid.AttrWrap(hdr, 'header')
        ftr = urwid.Text("Footer text")
        ftr = urwid.AttrWrap(ftr, 'footer')
        #container = urwid.Frame(header=hdr, body=w, footer=ftr)

        cb = urwid.CheckBox("hoi", False)
        cb.set_label(('right', 'test'))
        container = urwid.BoxAdapter(lst, 80)
        container = urwid.Filler(
                        urwid.Padding( container, align='center', width=('relative',50))
#                       , height=('relative',50)
                    )

        loop = urwid.MainLoop(container, palette, unhandled_input=show_or_exit)
        loop.run()

    def test_dump():
        for tree in conf.trees.values():
            for path, item_list in tree.get_items_by_path().items():
                print(path)

                for item in item_list:
                    print(item.name + ' = ' + str(item))

                print
