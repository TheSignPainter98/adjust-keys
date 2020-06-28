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
from util import key_subst, rem


def parse_layout(layout_row_profiles:[str], layout: [[dict]]) -> [dict]:
    seenKeys: 'str->int' = {}
    if len(layout_row_profiles) < len(layout):
        die('Insufficient information about what profile part each row has (e.g. the top row might be r5: got %d but needed at least %d' %(len(layout_row_profiles), len(layout)))

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

            ret = {'key': str(key_name(key))}
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

        if 'dim-x' not in ret and 'dim-y' not in ret:
            if 'key' not in ret or key == '':
                printw("Key \"%s\" %s 'key' field, please put one in" %
                       (str(key), 'missing' if key != '' else 'has empty'))
                ret['key'] = 'SOME_ID'

            if ret['key'] in seenKeys.keys():
                seenKeys[ret['key']] += 1
                ret['key'] = ret['key'] + '-' + str(seenKeys[ret['key']])
            else:
                seenKeys[ret['key']] = 1

        return ret

    if type(layout) != list and type(layout[0]) != list:
        die('Expected a list of lists in the layout (see the JSON output of KLE)'
            )

    parsed_layout: [dict] = []
    row: int = 0
    numDeltaY: int = 0
    lineInd:int = 0
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
            key['profile-part'] = layout_row_profiles[lineInd]
            if 'dim-y' in key:
                # Assume that if dim-y is present there is no corresponding key
                row += key['dim-y']
                col = 0
                numDeltaY -= 1
            else:
                col += key['width']
                if 'dim-x' not in key:
                    # Assume that if dim-x is present there is no corresponding key
                    parsed_layout += [key]
                    numDeltaX += 1

        numDeltaY += 1
        if 'dim-y' not in line[-1]:
            row += 1
        lineInd += 1

    return parsed_layout
