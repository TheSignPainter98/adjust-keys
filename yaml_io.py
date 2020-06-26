# Copyright (C)  Edward Jones
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

from log import printe
from os.path import exists
from sys import stdin
from yaml import dump, FullLoader, load

##
# @brief Read yaml from a given file or '-' for stdin. Exits on error
#
# @param fname:str Name of the file to use
#
# @return The data present in file fname
def read_yaml(fname:str) -> dict:
    if fname == '-':
        printi('Reading %s from stdin, please either type something or redirect a file in here' % fname)
        return load(stdin, Loader=FullLoader)
    else:
        if exists(fname):
            with open(fname, 'r') as f:
                return load(f, Loader=FullLoader)
        else:
            printe('Failed to read file "%s"' % fname)
            exit(1)

##
# @brief Write a dictionary to a given file, or '-' for stdout
#
# @param fname:str Name of file to write data into or '-' for stdout
# @param data:dict Data to write
#
# @return Nothing
def write_yaml(fname:str, data:dict):
    if fname == '-':
        print(dump(data), end='')
    else:
        with open(fname, 'w+') as f:
            print(dump(data), file=f, end='')

