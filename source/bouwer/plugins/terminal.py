# Copyright: 2008 Nadia Alramli
# License: BSD
 
"""Terminal controller module
Example of usage:
    print BG_BLUE + 'Text on blue background' + NORMAL
    print BLUE + UNDERLINE + 'Blue underlined text' + NORMAL
    print BLUE + BG_YELLOW + BOLD + 'text' + NORMAL
"""

import sys
import curses

# The current module
MODULE = sys.modules[__name__]

COLORS = "BLUE GREEN CYAN RED MAGENTA YELLOW WHITE BLACK".split()
# List of terminal controls, you can add more to the list.
CONTROLS = {
    'BOL':'cr', 'UP':'cuu1', 'DOWN':'cud1', 'LEFT':'cub1', 'RIGHT':'cuf1',
    'CLEAR_SCREEN':'clear', 'CLEAR_EOL':'el', 'CLEAR_BOL':'el1',
    'CLEAR_EOS':'ed', 'BOLD':'bold', 'BLINK':'blink', 'DIM':'dim',
    'REVERSE':'rev', 'UNDERLINE':'smul', 'NORMAL':'sgr0',
    'HIDE_CURSOR':'cinvis', 'SHOW_CURSOR':'cnorm'
}

# List of numeric capabilities
VALUES = {
    'COLUMNS':'cols', # Width of the terminal (None for unknown)
    'LINES':'lines',  # Height of the terminal (None for unknown)
    'MAX_COLORS': 'colors',
}

def default():
    """Set the default attribute values"""
    for color in COLORS:
        setattr(MODULE, color, '')
        setattr(MODULE, 'BG_%s' % color, '')
    for control in CONTROLS:
        setattr(MODULE, control, '')
    for value in VALUES:
        setattr(MODULE, value, None)

def setup():
    """Set the terminal control strings"""

    # Initializing the terminal
    curses.setupterm()
    # Get the color escape sequence template or '' if not supported
    # setab and setaf are for ANSI escape sequences
    bgColorSeq = curses.tigetstr('setab') or curses.tigetstr('setb') or ''
    fgColorSeq = curses.tigetstr('setaf') or curses.tigetstr('setf') or ''
 
    for color in COLORS:
        # Get the color index from curses
        colorIndex = getattr(curses, 'COLOR_%s' % color)

        # Try to retrieve the color escape sequence with TypeError workaround.
        # See http://bugs.python.org/issue10570
        try:
            bg_color_escape = curses.tparm(bgColorSeq, colorIndex)
            fg_color_escape = curses.tparm(fgColorSeq, colorIndex)
        except TypeError:
            bg_color_escape = curses.tparm(bgColorSeq.decode("utf-8"), colorIndex)
            fg_color_escape = curses.tparm(fgColorSeq.decode("utf-8"), colorIndex)

        # Set the color escape sequence after filling the template with index
        setattr(MODULE, color, fg_color_escape.decode("utf-8"))

        # Set background escape sequence
        setattr(
            MODULE, 'BG_%s' % color, bg_color_escape.decode("utf-8")
        )
    for control in CONTROLS:
        # Set the control escape sequence
        cstr = curses.tigetstr(CONTROLS[control]) or b''
        setattr(MODULE, control, cstr.decode("utf-8"))

    for value in VALUES:
        # Set terminal related values
        setattr(MODULE, value, curses.tigetnum(VALUES[value]))

def render(text):
    """Helper function to render text easily
    Example:
    render("%(GREEN)s%(BOLD)stext%(NORMAL)s") -> a bold green text
    """
    return text % MODULE.__dict__

setup()
