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
from util import dict_union, key_subst, rem, safe_get


def parse_layout(layout_row_profiles:[str], layout: [[dict]]) -> [dict]:
    seenKeys: 'str->int' = {}
    if len(layout_row_profiles) < len(layout):
        die('Insufficient information about what profile part each row has (e.g. the top row might be r5: got %d but needed at least %d' %(len(layout_row_profiles), len(layout)))

    def parse_key(key: 'either str dict', nextKey: 'maybe (either str dict)') -> [int,dict]:
        ret: dict
        shift: int = 1
        if type(key) == str:
            parts:[str] = list(reversed(key.split('\n')))
            alphaNums:[str] = list(filter(lambda p: match(r'[A-Za-z0-9]+\Z', p), parts))
            ret = { 'key': str(alphaNums[0] if alphaNums != [] else str(max(parts, default=0, key=len))) }
        elif type(key) == dict:
            if nextKey and type(nextKey) == str:
                ret = dict_union(key, { 'key': nextKey })
                shift = 2
            else:
                ret = dict(key)
        else:
            die('Malformed data when reading %s and %s' %(str(key), str(layout)))

        if 'key-type' not in ret:
            ret_key:str = safe_get(ret, 'key')
            if safe_get(ret, 'x') == 0.25 \
                and safe_get(ret, 'a') == 7 \
                and safe_get(ret, 'w') == 1.25 \
                and safe_get(ret, 'h') == 2 \
                and safe_get(ret, 'w2') == 1.5 \
                and safe_get(ret, 'h2') == 1 \
                and safe_get(ret, 'x2') == -0.25:
                    ret['key-type'] = 'iso-enter'
                    printw(ret['key-type'])
            elif ret_key == '+' and safe_get(ret, 'h') == 2:
                    ret['key-type'] = 'num-plus'
                    printw(ret['key-type'])
            elif ret_key and ret_key.lower() == 'enter' and safe_get(ret, 'h') == 2:
                    ret['key-type'] = 'num-enter'
                    printw(ret['key-type'])

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
            printi(ret)
            if 'key' not in ret:
                printw("Key \"%s\" %s 'key' field, please put one in" %
                       (str(key), 'missing' if key != '' else 'has empty'))
                ret['key'] = 'SOME_ID'
            if ret['key'] in seenKeys.keys():
                seenKeys[ret['key']] += 1
                ret['key'] = ret['key'] + '-' + str(seenKeys[ret['key']])
            else:
                seenKeys[ret['key']] = 1

        if 'a' in key:
            printi('"%s" "%s" |-> %s' %(key, nextKey, ret), shift)
        return (shift, ret)

    if type(layout) != list and any(list(map(lambda l: type(l) != list, layout))):
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
        i:int = 0
        while i < len(line):
            printi('Operating on %s and %s' %(line[i], safe_get(line, i+1)))
            (shift, line[i]) = parse_key(line[i], safe_get(line, i+1))
            line[i]['col'] = col
            line[i]['row'] = row
            line[i]['num-dx'] = numDeltaX
            line[i]['num-dy'] = numDeltaY
            line[i]['profile-part'] = layout_row_profiles[lineInd]
            if 'dim-y' in line[i]:
                # Assume that if dim-y is present there is no corresponding key
                row += line[i]['dim-y']
                col = 0
                numDeltaY -= 1
            else:
                if 'dim-x' not in line[i]:
                    col += line[i]['width']
                    numDeltaX += 1
                else:
                    col += line[i]['dim-x']
                    line[i]['col'] = col
                    col += line[i]['width']
                if 'key' in line[i]:
                    parsed_layout += [line[i]]
            i += shift
        numDeltaY += 1
        if 'dim-y' not in line[-1]:
            row += 1
        lineInd += 1

    return parsed_layout
