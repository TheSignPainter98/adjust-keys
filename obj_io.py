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
from os.path import exists
from util import concat


def read_obj(cfile:str) -> [[str, [str]]]:
    if not exists(cfile):
        die('Failed to read keycap file "%s"' % cfile)
    rawCap:str
    with open(cfile, 'r') as f:
        rawCap:str = f.read()
    return parse_cap(rawCap)

def parse_cap(rawCap:str) -> [[str, [str]]]:
    parsed_cap:[[str, [str]]] = []
    for line in rawCap.split('\n'):
        if len(line) > 1:
            words:[str] = line.split(' ')
            parsed_cap.append(([words[0], words[1:]]))
    return parsed_cap

def write_obj(fname:str, data:[[str, [str]]]) -> None:
    objUnRaw:str = unparse_obj(data)
    print(data[:10])
    if fname == '-':
        print(objUnRaw)
    else:
        with open(fname, 'w+') as f:
            print(objUnRaw, file=f)

def unparse_obj(data:[[str, [str]]]) -> str:
    objUnRaw:str = ''
    for line in list(map(lambda l: ' '.join([l[0]] + l[1]) + '\n', data)):
        objUnRaw += line
    return objUnRaw
