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
from bouwer.config import *

try:
    import urwid
except:
    # TODO: this should not be required!
    sys.exit('urwid required')

class ConfigTreeWidget(urwid.TreeWidget):
    """ Display widget for leaf nodes """
    def get_display_text(self):
        value = self.get_node().get_value()

        if isinstance(value, Config):
            return value.get_key('title', value.name)
        if isinstance(value, Configuration):
            return 'Configuration'
        if isinstance(value, str):
            return value
        return str(value)

#    def keypress(self, size, key):
#        pass

#class ConfigNode(urwid.TreeNode):
#    """ Data storage object for leaf nodes """
#    def load_widget(self):
#        return ConfigTreeWidget(self)
#
#    def selectable(self):
#        return true

class ConfigParentNode(urwid.ParentNode):
    """ Data storage object for interior/parent nodes """

    def load_widget(self):
        """ Return widget for displaying us """
        return ConfigTreeWidget(self)

    def load_child_keys(self):
        """ Return list of child keys """
        item = self.get_value()
        conf = Configuration.Instance()
        child_lst = []

        if isinstance(item, ConfigList):
            for child_name in item.get_key('options', []):
                child = conf.get(child_name) # TODO: but which tree?????
                child_lst.append(child._path + ':' + child.name)

        if isinstance(item, ConfigTree):
            for path, item_list in item.get_items_by_path().items():

                if path not in child_lst:
                    child_lst.append(path + ':')

                for child in item_list:
                    if not child.get_key('in_list', None):
                        child_lst.append(path + ':' + child.name)


            #for childs in item.subitems.values():
            #    for child in childs:
            #        if not child.get_key('in_list', None) and child.name not in child_lst:
            #            child_lst.append(child.name)

        if isinstance(item, Configuration):
            for tree in item.trees.values():
                child_lst.append(tree.name)

        if isinstance(item, list):
            pass

        return child_lst

    def load_child_node(self, key):
        """ Return child for the given key """
        value = self.get_value()

        if isinstance(value, ConfigTree) or \
           isinstance(value, ConfigList):
            path, name = key.split(':')

            if name:
                conf = Configuration.Instance()
                saved_active = conf.active_dir
                conf.active_dir = path
                child = conf.get(name)
                conf.active_dir = saved_active
            else:
                child = path
                name = path

            return ConfigParentNode(child, parent=self, key=key, depth = self.get_depth() + 1)

        if isinstance(value, Configuration):
            return ConfigParentNode(value.get(key), parent=self, key=key, depth = self.get_depth() + 1)

        if isinstance(value, str):
            return ConfigParentNode(key, parent=self, key=key, depth = self.get_depth() + 1)

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

        root_node = self.conf
        TreeBrowser(root_node).main()
        #self.test_dump()

    def test_dump(self):
        for tree in self.conf.trees.values():
            for path, item_list in tree.get_items_by_path().items():
                print(path)

                for item in item_list:
                    print(item.name + ' = ' + str(item))

                print

class TreeBrowser:
    palette = [
        ('body', 'black', 'light gray'),
        ('focus', 'light gray', 'dark blue', 'standout'),
        ('head', 'yellow', 'black', 'standout'),
        ('foot', 'light gray', 'black'),
        ('key', 'light cyan', 'black','underline'),
        ('title', 'white', 'black', 'bold'),
        ('flag', 'dark gray', 'light gray'),
        ('error', 'dark red', 'light gray'),
        ]

    footer_text = [
        ('title', "Example Data Browser"), "    ",
        ('key', "UP"), ",", ('key', "DOWN"), ",",
        ('key', "PAGE UP"), ",", ('key', "PAGE DOWN"),
        "  ",
        ('key', "+"), ",",
        ('key', "-"), "  ",
        ('key', "LEFT"), "  ",
        ('key', "HOME"), "  ",
        ('key', "END"), "  ",
        ('key', "Q"),
        ]

    def __init__(self, data=None):
        self.topnode = ConfigParentNode(data)
        self.listbox = urwid.TreeListBox(urwid.TreeWalker(self.topnode))
        self.listbox.offset_rows = 1
        self.header = urwid.Text( "" )
        self.footer = urwid.AttrWrap( urwid.Text( self.footer_text ),
            'foot')
        self.view = urwid.Frame(
            urwid.AttrWrap( self.listbox, 'body' ),
            header=urwid.AttrWrap(self.header, 'head' ),
            footer=self.footer )

    def main(self):
        """Run the program."""

        self.loop = urwid.MainLoop(self.view, self.palette,
                                   unhandled_input=self.unhandled_input)
        self.loop.run()

    def unhandled_input(self, k):
        if k in ('q','Q'):
            raise urwid.ExitMainLoop()


def get_example_tree():
    """ generate a quick 100 leaf tree for demo purposes """
    retval = {"name":"parent","children":[]}
    for i in range(10):
        retval['children'].append({"name":"child " + str(i)})
        retval['children'][i]['children']=[]
        for j in range(10):
            retval['children'][i]['children'].append({"name":"grandchild " +
                                                      str(i) + "." + str(j)})
    return retval
