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

from log import die, printi, printw
from re import match
from util import append, key_subst, rem


def parse_layout(layout: [[dict]]) -> [dict]:
    seenKeys: 'str->int' = {}

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
            ret = key_subst(ret, 'x', 'dim-x')
        if 'y' in ret:
            ret = key_subst(ret, 'y', 'dim-y')
        if 'w' in ret:
            ret = key_subst(ret, 'w', 'width')
        else:
            ret['width'] = 1.0
        if 'h' in ret:
            ret = key_subst(ret, 'h', 'height')
        else:
            ret['height'] = 1.0

        #  if ('id' not in ret or key == '') and ('dim-x' not in ret and 'dim-y' not in ret):
        if 'dim-x' not in ret and 'dim-y' not in ret:
            if 'id' not in ret or key == '':
                printw("Key \"%s\" %s 'id' field, please put one in" %
                       (str(key), 'missing' if key != '' else 'has empty'))
                ret['id'] = 'SOME_ID'

            if ret['id'] in seenKeys.keys():
                seenKeys[ret['id']] += 1
                ret['id'] = ret['id'] + '-' + str(seenKeys[ret['id']])
            else:
                seenKeys[ret['id']] = 1

        return ret

    if type(layout) != list and type(layout[0]) != list:
        die('Expected a list of lists in the layout (see the JSON output of KLE)'
            )

    parsed_layout: [dict] = []
    row: int = 0
    numDeltaY: int = 0
    for line in layout:
        col: int = 0
        prevCol: int = 0
        numDeltaX: int = 0
        for key in line:
            key = parse_key(key)
            printi('Operating on %s' % key)
            key['col'] = col
            key['row'] = row
            key['num-dx'] = numDeltaX
            key['num-dy'] = numDeltaY
            if 'dim-y' in key:
                # Assume that if dim-y is present there is no corresponding key
                row += key['dim-y']
                col = 0
                # Assume that if x is present there is no corresponding key
                # Gee, a functor type class would really help here, you know? But that would require Python to have a decent type system and let's face it that'll probably never happen.
            else:
                col += key['width']
                if 'dim-x' not in key:
                    # Assume that if dim-x is present there is no corresponding key
                    parsed_layout += [key]
                    numDeltaX += 1

        if 'dim-y' not in line[-1]:
            row += 1
            numDeltaY += 1

    return parsed_layout
