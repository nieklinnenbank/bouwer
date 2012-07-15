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

def Library(self, target, sources):
    print("Building Library `" + target + "' from `" + str(sources) + "'")

    n = len(sources) + 1
    i = 1

    for src in sources:
        #print(self['cc'] + ' ' + self['ccflags'] + ' -c -o ' + src + '.o ' +  src)
        print('[' + str(i) + '/' + str(n) + ']  CC  ' + src)
        i = i + 1

    print('[' + str(n) + '/' + str(n) + ']  AR  ' + target)
