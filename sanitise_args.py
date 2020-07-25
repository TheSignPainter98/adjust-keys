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
from log import die
from sys import argv
from util import concat, flatten_list

def sanitise_args(pname:str, args) -> list:
    global argv
    if type(args) == tuple:
        args = list(args)
    if args == ['']:
        args = []
    args = flatten_list(args)
    if type(args) == list and all(map(lambda a: type(a) == str, args)):
        args = list(reduce(concat, map(lambda a: a.split(' '), args), []))
    elif type(args) == str:
        args = args.split(' ')
    else:
        die('Unknown argument type, %s received, please use a list of (lists of) strings or just a single string' % str(type(args)))
    # Put executable name on the front if it is absent (e.g. if called from python with only the arguments specified)
    if len(args) == 0 or args[0] != argv[0]:
        if len(args) == 0:
            argv.append(pname)
        elif not argv[0].startswith('blender'):
            argv[0] = pname
        args = [argv[0]] + list(args)

    return args

def arg_inf(dargs:dict, key:str, msg:str=None) -> str:
    return ' (default: %s%s, yaml-option-file-key: %s)' % (dargs[key], ' ' + msg if msg else '', key)
