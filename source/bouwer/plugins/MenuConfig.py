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
    from urwid import *
except:
    # TODO: this should not be required!
    class TreeWidget: pass
    class ParentNode: pass

class ConfigTreeWidget(TreeWidget):
    """ Display widget for leaf nodes """

    def __init__(self, node):
        value = node.get_value()

        if isinstance(value, ConfigBool):
            un_icon = '[ ]'
            ex_icon = '[*]'
        else:
            un_icon = ex_icon = '  '

        self.unexpanded_icon = SelectableIcon(un_icon, 0)
        self.expanded_icon = SelectableIcon(ex_icon, 0)

        super(ConfigTreeWidget, self).__init__(node)

    def __getattribute__(self, name):
        """
        Override the self.expanded with the actual ConfigBool.value()
        """
        if name == 'expanded':
            item = object.__getattribute__(self, 'get_node')().get_value()

            if isinstance(item, ConfigBool):
                return item.value()

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name == 'expanded':
            item = self.get_node().get_value()

            if isinstance(item, ConfigBool):
                item.update(value)

        self.__dict__[name] = value

    def get_indented_widget(self):
        widget = self.get_inner_widget()
        if not self.is_leaf:
            widget = Columns([('fixed', 3,
                [self.unexpanded_icon, self.expanded_icon][self.expanded]),
                widget], dividechars=1)
        indent_cols = self.get_indent_cols()
        return Padding(widget,
            width=('relative', 100), left=indent_cols)

    def get_display_text(self):
        value = self.get_node().get_value()

        if isinstance(value, Config):
            return value.get_key('title', value.name) + ' (' + str(value.value()) + ')'
        if isinstance(value, Configuration):
            return 'Configuration'
        if isinstance(value, str):
            return value
        return str(value)

    def keypress(self, size, key):
        if self.is_leaf:
            return key
        if key == "enter":
            self.expanded = not self.expanded
            self.update_expanded_icon()
        elif key in ("+", "right"):
            self.expanded = True
            self.update_expanded_icon()
        elif key == "-":
            self.expanded = False
            self.update_expanded_icon()
        elif self._w.selectable():
            return self.__super.keypress(size, key)
        else:
            return key

class ConfigParentNode(ParentNode):
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

        # We want trees to evaluate to True in the DEFAULT tree, only during edits.
        # This makes sure that ConfigBool's do not all get False in the DEFAULT tree,
        # because they may have a 'depends on MY_TREE' which will be False in the DEFAULT tree otherwise.
        self.conf.edit_mode = True

        root_node = self.conf
        TreeBrowser(root_node).main()
        #self.test_dump()
        self.conf.edit_mode = False

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
        self.listbox = TreeListBox(TreeWalker(self.topnode))
        self.listbox.offset_rows = 1
        self.header = Text( "" )
        self.footer = AttrWrap( Text( self.footer_text ),
            'foot')
        self.view = Frame(
            AttrWrap( self.listbox, 'body' ),
            header=AttrWrap(self.header, 'head' ),
            footer=self.footer )

    def main(self):
        """Run the program."""

        self.loop = MainLoop(self.view, self.palette,
                                   unhandled_input=self.unhandled_input)
        self.loop.run()

    def unhandled_input(self, k):
        if k in ('q','Q'):
            raise ExitMainLoop()


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
