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

import json
import collections
import logging
import os
import pickle

"""
Bouwer generic utilities
"""

BOUWTEMP = '.bouwtemp'

def tempfile(filename):
    """
    Create a temporary builder file
    """
    try:
        os.stat(BOUWTEMP)
    except:
        os.mkdir(BOUWTEMP)
    return BOUWTEMP + '/' + filename

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

    # TODO: this goes WRONG if the path to the class isnt the same everywhere... make a test case also.
    # e.g. import compiler
    # e.g. import bouwer.plugins.compiler
    # leads to very subtile errors

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

class AsciiDecoder(json.JSONDecoder):
    """
    Translate JSON to python objects in ASCII instead of Unicode.
    """

    def __init__(self, encoding=None, object_hook=None, parse_float=None,
                       parse_int=None, parse_constant=None, strict=True,
                       object_pairs_hook=collections.OrderedDict):
        """
        Class constructor.

        Uses an OrderedDict to preserve the order of JSON items read from file.
        """
        super(AsciiDecoder, self).__init__(
                encoding=encoding,
                object_hook=object_hook,
                parse_float=parse_float,
                parse_int=parse_int,
                parse_constant=parse_constant,
                strict=strict,
                object_pairs_hook=object_pairs_hook)

    def decode(self, json_string):
        """
        Called to decode a json string to python object.
        """
        data = super(AsciiDecoder, self).decode(json_string)
        return self.convert(data)

    def convert(self, data):
        """
        Convert unicode strings to ascii
        """
        #return data

        if isinstance(data, dict) or isinstance(data, collections.OrderedDict):
            d = collections.OrderedDict()

            for key, value in data.iteritems():
                d[self.convert(key)] = self.convert(value)
            return d
        elif isinstance(data, list):
            return [self.convert(element) for element in data]
        elif isinstance(data, unicode):
            return data.encode('utf-8')
        else:
            return data

class Cache(object):
    """
    Generic caching implementation
    """

    """ List of Cache instances """
    instances = {}

    def __init__(self, name):
        """
        Class constructor
        """
        self.log = logging.getLogger(__name__)
        self.name = name
        self.data = {}
        self.filename = tempfile(self.name + '.cache')

        try:
            self.fp = open(self.filename, 'r+')
        except IOError:
            self.fp = open(self.filename, 'w+')

        self.stat = os.stat(self.filename)
        
        try:
            self.data = pickle.load(self.fp)
        except EOFError:
            self.data = {} 

        self.log.debug('Cache ' + self.name + ' : created')

    def __del__(self):
        """
        Class destructor
        """
        self.flush()
        self.fp.close()
        self.log.debug('Cache ' + str(self.name) + ' : destroyed')

    @classmethod
    def Instance(cls, name):
        """
        Retrieve instance of a Cache
        """
        if name not in Cache.instances:
            Cache.instances[name] = Cache(name)
        
        return Cache.instances[name]

    @classmethod
    def FlushAll(cls):
        """
        Flush all instances
        """
        for inst in Cache.instances:
            Cache.instances[inst].flush()
            Cache.instances[inst].fp.close()

    def get(self, key):
        try:
            return self.data[key]
        except:
            return None

    def put(self, key, value):
        self.log.debug('Cache ' + self.name + ' : ' + key + ' => ' + str(value))
        self.data[key] = value

    def flush(self):
        pickle.dump(self.data, self.fp)
        self.fp.flush()

    def timestamp(self):
        return self.stat.st_mtime

