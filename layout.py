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
from log import die, printi, printw
from re import match
from util import append, rem


class Layout:
    def __init__(self, layout: dict):
        def parse_key(key: 'either str dict') -> dict:
            ret: dict
            if type(key) == str:

                def key_name(name: str) -> str:
                    parts = list(reversed(key.split('\n')))
                    alphaNums = list(
                        filter(lambda p: match(r'[A-Za-z0-9]+\Z', p), parts))
                    if alphaNums != []:
                        return alphaNums[0]
                    else:
                        return max(parts, default=0, key=len)

                ret = {'id': str(key_name(key))}
            elif type(key) == dict:
                ret = dict(key)
            else:
                die('Unknown key type entered: %s' % type(key))

            if 'x' in ret:
                ret = rem(ret, 'x')

            if 'w' in ret:
                ret['width'] = float(ret['w'])
                del ret['w']
            else:
                ret['width'] = 1.0

            if 'h' in ret:
                ret['height'] = float(ret['h'])
                del ret['h']
            else:
                ret['height'] = 1.0

            if 'id' not in ret or key == '':
                ret['id'] = 'SOME_ID'
                printw("Key \"%s\" %s 'id' field, please put one in" %
                       (str(key), 'missing' if key != '' else 'has empty'))

            if ret['id'] in self.seenKeys.keys():
                self.seenKeys[ret['id']] += 1
                ret['id'] = ret['id'] + '-' + str(self.seenKeys[ret['id']])
            else:
                self.seenKeys[ret['id']] = 1

            return ret

        if type(layout) != list and type(layout[0]) != list:
            die('Expected a list of lists in the layout (see the JSON output of KLE)'
                )

        self.seenKeys: 'str->int' = {}
        self.layout: [Group] = []
        row: int = 0
        for line in layout:
            col: int = 0
            prevCol:int = 0
            groupContent: [[dict]] = []
            prevSlice: int = 0
            for i in range(0, len(line)):
                if 'y' in line[i]:
                    # Assume that if y is present there is no corresponding key
                    row += line[i]['y']
                    col = -1
                if 'x' in line[i]:
                    # Assume that if x is present there is no corresponding key
                    # Gee, a functor type class would really help here, you know? But that would require Python to have a decent class system and let's face it that'll probably never happen.
                    self.layout += [Group((row, prevCol), list(map(parse_key, line[prevSlice:i])))]
                    prevSlice = i + 1
                    col += line[i]['x']
                    prevCol = col
                else:
                    col += line[i]['w'] if 'w' in line[i] else 1
            if 'x' not in line[-1]:
                self.layout += [Group((row, prevCol), list(map(parse_key, line[prevSlice:])))]
            row += 1

        for g in self.layout:
            print(g)


    def __str__(self) -> str:
        return str(self.layout)


class Group:
    def __init__(self, pos: [int, int], keys: [dict]):
        self.pos = pos
        self.keys = keys

    def __str__(self) -> str:
        return str(self.pos) + ' |-> ' + str(self.keys)
