#!/usr/bin/python
#
# Copyright (C) 2012 Niek Linnenbank <nieklinnenbank@gmail.com>
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

def write_hello_func(number):
    """
    Generate a hello function labeled with the given number
    """
    fp = open('hello' + str(number) + '.c', 'w')
    fp.write("""
             #include <stdio.h>

             void hello_""" + str(number) + """()
             {
                 printf("Hello, %d!", """ + str(number) + """);
             }
             """)
    fp.close()

def write_hello_world(number):
    """
    Generate a hello world program with the give number of hello()'s
    """
    fp = open('main.c', 'w')

    for i in range(number):
        fp.write("void hello_" + str(i) + "();" + os.linesep)

    fp.write("""
             int main(void)
             {
             """)

    for i in range(number):
        fp.write("hello_" + str(i) + "();" + os.linesep)

    fp.write("return 0; }")
    fp.close()

def generate_hello_program(count):
    """
    Generate a hello world program with the given number of hello()'s
    """

    # Generate C files
    for i in range(count):
        write_hello_func(i)
    write_hello_world(count)

if __name__ == '__main__':
    generate_hello_program(int(sys.argv[1]))

