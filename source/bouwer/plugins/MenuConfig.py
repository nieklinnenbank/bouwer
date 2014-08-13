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
import urwid
from bouwer.plugin import Plugin
from bouwer.config import *

loop = None
view = None

class ConfigListTree(urwid.TreeWidget):
    # This class shows the contents of a list as a tree too.
    # The items are the nodes, and the keywords are the childs of each item.
    pass

class ConfigListWidget(urwid.PopUpLauncher):
    #
    # This contains a Button (and the selected item in text), which will create a PopUp
    # to a ConfigListTree, to modify the ConfigList and its items when selected.
    #
    pass

class DialogExit(Exception):
    pass

class DialogDisplay:
    palette = [
        ('body','black','light gray', 'standout'),
        ('border','black','dark blue'),
        ('shadow','white','black'),
        ('selectable','black', 'dark cyan'),
        ('focus','white','dark blue','bold'),
        ('focustext','light gray','dark blue'),
        ]

    def __init__(self, text, height, width, body=None, loop=None, parent=None):
        width = int(width)
        if width <= 0:
            width = ('relative', 80)
        height = int(height)
        if height <= 0:
            height = ('relative', 80)

        self.body = body
        if body is None:
           # fill space with nothing
           body = urwid.Filler(urwid.Divider(),'top')

        self.frame = urwid.Frame( body, focus_part='footer')
        if text is not None:
            self.frame.header = urwid.Pile( [urwid.Text(text),
                urwid.Divider()] )
        w = self.frame

        # pad area around listbox
        w = urwid.Padding(w, ('fixed left',2), ('fixed right',2))
        w = urwid.Filler(w, ('fixed top',1), ('fixed bottom',1))
        w = urwid.AttrWrap(w, 'body')

        # "shadow" effect
        w = urwid.Columns( [w,('fixed', 2, urwid.AttrWrap(
            urwid.Filler(urwid.Text(('border','  ')), "top")
            ,'shadow'))])
        w = urwid.Frame( w, footer =
            urwid.AttrWrap(urwid.Text(('border','  ')),'shadow'))

        # outermost border area
        w = urwid.Padding(w, 'center', width )
        w = urwid.Filler(w, 'middle', height )
        w = urwid.AttrWrap( w, 'border' )

        self.parent = parent
        self.loop = loop
        self.view = w

    def add_buttons(self, buttons):
        l = []
        for name, exitcode in buttons:
            b = urwid.Button( name, self.button_press )
            b.exitcode = exitcode
            b = urwid.AttrWrap( b, 'selectable','focus' )
            l.append( b )
        self.buttons = urwid.GridFlow(l, 10, 3, 1, 'center')
        self.frame.footer = urwid.Pile( [ urwid.Divider(),
            self.buttons ], focus_item = 1)

    def button_press(self, button):
        if self.parent is None:
            raise DialogExit(button.exitcode)
        else:
            self.loop.widget=self.parent                # !!!! THERE IT IS!!!!!

    def show(self):
        if self.loop is None:
            self.loop = urwid.MainLoop(self.view, self.palette)
            try:
                self.loop.run()
            except DialogExit, e:
                return self.on_exit( e.args[0] )
        else:
            self.loop.widget = self.view

    def on_exit(self, exitcode):
        return exitcode, ""

class InputDialogDisplay(DialogDisplay):
    def __init__(self, item, caller, height, width, parent, loop):
        self.edit = urwid.Edit(multiline=True, edit_text=item.value()) # TODO: tree???
        self.item = item
        self.caller = caller
        body = urwid.ListBox([self.edit])
        body = urwid.AttrWrap(body, 'selectable','focustext')
        DialogDisplay.__init__(self, item.name, height, width, body, parent, loop)
        self.frame.set_focus('body')
        urwid.connect_signal(self.edit, 'change', self.input_change)

    def input_change(self, widget, text):
        if text.endswith("\n"):
            self.item.update(str(text.rstrip()))
            self.loop.widget = self.parent
            self.caller._w.base_widget.widget_list[1].set_text(self.caller.get_display_text())
            self.caller._invalidate()

    def on_exit(self, exitcode):
        return exitcode, self.edit.get_edit_text()

class ConfigMenuWidget(urwid.TreeWidget):
    #
    # This widget represents a menu defined in a Bouwconfig.
    # If selected, it should open a new Overlay(?) with a new tree view, starting
    # with the childs registered in that menu...
    #
    pass

class ConfigStringWidget(urwid.TreeWidget):
    def get_display_text(self):
        item = self.get_node().get_value()
        return item.get_key('title', item.name) + ' (' + str(item.value()) + ')' # TODO: the tree!!!
    def keypress(self, size, key):
        item = self.get_node().get_value()
        if key == "enter":
            d = InputDialogDisplay(item, self, 9, 100, loop, view)
            d.add_buttons([("OK", 0)])
            d.show()
            self.update_expanded_icon()
        elif self._w.selectable():
            return self.__super.keypress(size, key)
        else:
            return key

# TODO: ConfigBoolWidget(TreeWidget)
# only for ConfigBools... (and ConfigTree also?)
class ConfigTreeWidget(urwid.TreeWidget):
    """ Display widget for leaf nodes """

    def __init__(self, node):
        value = node.get_value()

        if isinstance(value, ConfigBool):
            un_icon = '[ ]'
            ex_icon = '[*]'
        else:
            un_icon = ex_icon = '  '

        self.unexpanded_icon = urwid.SelectableIcon(un_icon, 0)
        self.expanded_icon = urwid.SelectableIcon(ex_icon, 0)

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
            widget = urwid.Columns([('fixed', 3,
                [self.unexpanded_icon, self.expanded_icon][self.expanded]),
                widget], dividechars=1)
        indent_cols = self.get_indent_cols()
        return urwid.Padding(widget,
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
        elif key in ("+", "right", "y"):
            self.expanded = True
            self.update_expanded_icon()
        elif key in ("-", "n"):
            self.expanded = False
            self.update_expanded_icon()
        elif self._w.selectable():
            return self.__super.keypress(size, key)
        else:
            return key

class ConfigMenuNode(urwid.ParentNode):
    """
    Represents a Bouwconfig 'menu' entry in urwid.
    """

    def load_widget(self):
        return ConfigTreeWidget(self)
    def load_child_keys(self):
        return []

class ConfigListNode(urwid.ParentNode):
    """
    Represents a ConfigList in urwid.
    """

    def load_widget(self):
        return ConfigTreeWidget(self)

    def load_child_keys(self):
        child_lst = []
        conf = Configuration.Instance()

        for child_name in self.get_value().get_key('options', []):
            child = conf.get(child_name) # TODO: but which tree?????
            child_lst.append(child._path + ':' + child.name)
        return child_lst

    def load_child_node(self, key):
        path, name = key.split(':')

        conf = Configuration.Instance()
        saved_active = conf.active_dir
        conf.active_dir = path
        child = conf.get(name) # TODO: but which tree???
        conf.active_dir = saved_active

        return ConfigBoolNode(child, parent=self, key=key, depth = self.get_depth() + 1)

class ConfigBoolNode(urwid.ParentNode):
    """
    Represents a ConfigBool in urwid.
    """

    def load_widget(self):
        return ConfigTreeWidget(self)
    def load_child_keys(self):
        # TODO: must have our keywords as child...
        return []

class ConfigStringNode(urwid.ParentNode):
    """
    Represents a ConfigString in urwid.
    """
    def load_widget(self):
        return ConfigStringWidget(self)
    def load_child_keys(self):
        # TODO: must have our keywords a child... (same a ConfigBoolNode, inherit please)
        return []

class ConfigTreeNode(urwid.ParentNode):
    """
    Represents a ConfigTree in urwid.
    """

    def load_widget(self):
        return ConfigTreeWidget(self)

    def load_child_keys(self):
        child_lst = []
        for path, item_list in self.get_value().get_items_by_path().items():
            if path not in child_lst:
                child_lst.append(path + ':')

            for child in item_list:
                if not child.get_key('in_list', None):
                    child_lst.append(path + ':' + child.name)
        return child_lst

    def load_child_node(self, key):
        path, name = key.split(':')

        if name:
            conf = Configuration.Instance() 
            saved_active = conf.active_dir
            conf.active_dir = path
            child = self.get_value().get(name)
            conf.active_dir = saved_active
        else:
            child = path
            name = path

        if isinstance(child, ConfigBool):
            return ConfigBoolNode(child, parent=self, key=key, depth=self.get_depth() + 1)
        elif isinstance(child, ConfigList):
            return ConfigListNode(child, parent=self, key=key, depth=self.get_depth() + 1)
        elif isinstance(child, ConfigString):
            return ConfigStringNode(child, parent=self, key=key, depth=self.get_depth() + 1)
        elif isinstance(child, str):
            return ConfigMenuNode(child, parent=self, key=key, depth = self.get_depth() + 1)
        else:
            raise Exception("unknown child type: " + str(type(child)))

class ConfigurationNode(urwid.ParentNode):
    """
    Represents a Configuration in a urwid TreeList
    """

    def load_widget(self):
        return ConfigTreeWidget(self)

    def load_child_keys(self):
        child_lst = []
        for tree in self.get_value().trees.values():
            child_lst.append(tree.name)
        return child_lst

    def load_child_node(self, key):
        return ConfigTreeNode(self.get_value().get(key), parent=self, key=key, depth = self.get_depth() + 1)

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

        # We want trees to evaluate to True in the DEFAULT tree, only during edits.
        # This makes sure that ConfigBool's do not all get False in the DEFAULT tree,
        # because they may have a 'depends on MY_TREE' which will be False in the
        # DEFAULT tree otherwise.
        self.conf.edit_mode = True
        self.open_urwid_editor()
        self.conf.edit_mode = False

        # TODO: ask for saving here

    def open_urwid_editor(self):

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

        topnode = ConfigurationNode(self.conf)
        listbox = urwid.TreeListBox(urwid.TreeWalker(topnode))
        listbox.offset_rows = 1
        header = urwid.Text( "Bouwer Configuration" )
        footer = urwid.AttrWrap( urwid.Text(footer_text ),
            'foot')

        global view, loop

        view = urwid.Frame(
            urwid.AttrWrap(listbox, 'body' ),
            header=urwid.AttrWrap(header, 'head' ),
            footer=footer )

        loop = urwid.MainLoop(view, palette,
                              unhandled_input=self.unhandled_input,
                              pop_ups=True)
        loop.run()

    def unhandled_input(self, k):
        global view, loop
        if k in ('q','Q'):
            raise urwid.ExitMainLoop()
        if k == 't':
            d = DialogDisplay1( "Hello", 50, 10, None, loop, view )
            d.add_buttons([    ("OK", 0), ("Cancel", 1) ])
            d.show()
        if k == 'r':
            d = InputDialogDisplay("test label", "test input text", 9, 100, loop, view)
            d.add_buttons([    ("OK", 0) ])
            d.show()
