#
# Copyright (C) 2014 Niek Linnenbank
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
import os.path
import glob
import random
import sys
import tarfile
from bouwer.config import *
from bouwer.builder import *
from bouwer.plugin import *

class Archive(Plugin):
    """
    Generate an archive
    """

    def execute_any(self, filename, include=['.'], exclude=['']):
        """ Builder implementation """

	basename, ext = os.path.splitext(filename)

	if ext in ['.tar', '.tar.gz',  '.tgz', '.gz']:
	    name   = 'TAR'
	    format = 'gz'
	elif ext in ['.tar.bz2', '.bz2', '.tbz']:
	    name   = 'TAR'
	    format = 'bz2'
	#elif ext in ['.zip']:
	#    name   = 'ZIP'
	#    format = 'zip'
	else:
	    raise Exception('archive format not supported: ' + filename)

	sources = self.get_filelist(filename, '.', include, exclude)

        # Schedule Action to compile it
        self.build.action(TargetPath(filename),
			  sources,
			  self.action_run,
                          pretty_name=name,
                          pretty_target=filename,
			  format=format)

    def action_run(self, action):
        """
        Run the given action
        """

	# split the target directory, filename, and stuffix
	base_name = action.target.split('.tar')[0]
	(target_dir, dir_name) = os.path.split(base_name)

	# create the target directory if it does not exist
	#if target_dir and not os.path.exists(target_dir):
	#    os.makedirs(target_dir)

	# open our tar file for writing
	tar = tarfile.open(action.target, "w:%s" % (action.tags['format'],))

	# write sources to our tar file
	for src in action.sources:
	    tar.add(src, '%s/%s' % (base_name, src))

	# all done
	tar.close()
	return 0

    def get_filelist(self, target, directory, include, exclude):

	filelist = []
	orig_dir = os.getcwd()
	orig_act = self.conf.active_dir
	os.chdir(directory)
	self.conf.active_dir += '/' + directory

	for inc in include:
	    # Exclude files
	    if inc in exclude:
		continue

	    exc_list = [ target ]
	    for exc in exclude:
		exc_list += glob.glob(exc)

	    # Is the include a directory?
	    if os.path.isdir(inc) :
	        filelist += self.get_filelist(target, inc, ['*'], exclude)

	    # Is the include a file?
	    elif os.path.isfile(inc) and inc not in exc_list:
	        filelist.append(SourcePath(inc))

	    # include is a pattern
	    else:
		for f in glob.glob(inc):
		    if os.path.isdir(f):
			filelist += self.get_filelist(target, f, include, exclude)
		    elif f not in exc_list:
			filelist.append(SourcePath(f))
	os.chdir(orig_dir)
	self.conf.active_dir = orig_act
	return filelist
