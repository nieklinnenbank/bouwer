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

class Singleton(object):
    """
    Singleton classes may have only one instance
    """

    @classmethod
    def _raise_direct(cls, *args, **kwargs):
        """
        Called when a :class:`.Singleton` is not accessed using `Instance`
        """
        raise Exception('Singletons may only be created with Instance()')

    @classmethod
    def Instance(cls, *args, **kwargs):
        """
        Called to lookup the :class:`.Singleton` instance
        """
        if '__class_obj__' in cls.__dict__:
            if len(args) > 0 or len(kwargs) > 0:
                raise Exception('singletons can only be initialized once')

            return cls.__class_obj__
        else:
            cls.__class_obj__ = cls.__new__(cls)
            
            # Overwrite callbacks to raise exception later
            init = cls.__class_obj__.__init__
            cls.__orig_init__ = cls.__init__
            cls.__init__ = cls._raise_direct

            # Invoke constructor
            init(*args, **kwargs)
        
        return cls.__class_obj__

    @classmethod
    def Destroy(cls):
        """
        Remove a :class:`.Singleton` instance
        """
        if '__class_obj__' in cls.__dict__:
            del cls.__class_obj__
            cls.__init__ = cls.__orig_init__

