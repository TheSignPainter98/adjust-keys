# Copyright (C) Edward Jones
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

from functools import reduce
from sys import argv
from util import concat, flatten_list

def sanitise_args(pname:str, args) -> list:
    # Handle arguments; accept string, list of strings and list of lists of strings
    if all(map(lambda a: type(a) == str, args)):
        args = list(reduce(concat, map(lambda a: a.split(' '), args)))
    args = flatten_list(args)
    if type(args) == tuple:
        args = list(args)
    # Put executable name on the front if it is absent (e.g. if called from python with only the arguments specified)
    if args[0] != argv[0]:
        if not argv[0].startswith('blender'):
            argv[0] = pname
        args = [argv[0]] + list(args)

    return args

