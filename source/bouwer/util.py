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

