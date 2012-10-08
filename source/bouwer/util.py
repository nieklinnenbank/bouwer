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

import bouwer.builder
import bouwer.config

# TODO: strict checks on the singleton please. Add exceptions

class Singleton(object):
    """
    Singleton classes may have only one instance
    """

    @classmethod
    def instance(classtype, *args, **kwargs):
        """
        Called to lookup the singleton instance
        """
        if classtype.exists():
            return classtype.__class_obj__
        else:
            classtype.__class_obj__ = classtype.__new__(classtype)
            classtype.__class_obj__.__init__(*args, **kwargs)
        
        return classtype.__class_obj__

    @classmethod
    def exists(classtype):
        """
        Check if the single instance exists
        """
        return '__class_obj__' in classtype.__dict__

class Path:

    def __init__(self, path):
        self.relative = path
        self.absolute = path
        self.build    = bouwer.builder.BuilderManager.instance()
        self.conf     = bouwer.config.Configuration.instance()

    def append(self, text):
        self.relative += text
        self.absolute += text

    def __str__(self):
        return str(self.absolute)

class SourcePath(Path):

    def __init__(self, path):
        super().__init__(path)
        self.absolute = self.build.translate_source(self.relative,
                                                    self.conf.active_tree)
        
class TargetPath(Path):

    def __init__(self, path):
        super().__init__(path)
        self.absolute = self.build.translate_target(self.relative,
                                                    self.conf.active_tree)

