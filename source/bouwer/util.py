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

"""
Bouwer generic utilities
"""

import bouwer.builder
import bouwer.config

# TODO: strict checks on the singleton please. Add exceptions

class Singleton(object):
    """
    Singleton classes may have only one instance
    """

    @classmethod
    def instance(cls, *args, **kwargs):
        """
        Called to lookup the singleton instance
        """
        if cls.exists():
            return cls.__class_obj__
        else:
            cls.__class_obj__ = cls.__new__(cls)
            cls.__class_obj__.__init__(*args, **kwargs)
        
        return cls.__class_obj__

    @classmethod
    def exists(cls):
        """
        Check if the single instance exists
        """
        return '__class_obj__' in cls.__dict__

class Path(object):
    """
    Abstract representation of a file path
    """

    def __init__(self, path):
        """ Constructor """
        self.relative = path
        self.absolute = path
        self.build    = bouwer.builder.BuilderManager.instance()
        self.conf     = bouwer.config.Configuration.instance()

    def append(self, text):
        """ Append text to the path """
        self.relative += text
        self.absolute += text

    def __str__(self):
        """ Convert path to string """
        return str(self.absolute)

class SourcePath(Path):
    """
    Implements a path to a source file
    """

    def __init__(self, path):
        super().__init__(path)
        self.absolute = self.build.translate_source(self.relative,
                                                    self.conf.active_tree)
        
class TargetPath(Path):
    """
    Implements a path to a target output file
    """

    def __init__(self, path):
        super().__init__(path)
        self.absolute = self.build.translate_target(self.relative,
                                                    self.conf.active_tree)

