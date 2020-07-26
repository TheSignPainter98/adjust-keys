# Copyright (C) Edward Jones

from log import die, printi, printw
from re import match
from util import dict_union, key_subst, rem, safe_get
from yaml_io import read_yaml


def get_layout(layout_file:str, layout_row_profile_file:str) -> [dict]:
    return parse_layout(read_yaml(layout_row_profile_file), read_yaml(layout_file))


def parse_layout(layout_row_profiles: [str], layout: [[dict]]) -> [dict]:
    printi('Reading layout information')
    if len(layout_row_profiles) < len(layout):
        printw(
            'Insufficient information about what profile part each row has (e.g. the top row might be r5: got %d but should have at least %d'
            % (len(layout_row_profiles), len(layout)))

    def parse_key(key: 'either str dict',
                  nextKey: 'maybe (either str dict)') -> [int, dict]:
        ret: dict
        shift: int = 1

        def parse_name(txt: str) -> str:
            parts: [str] = list(reversed(txt.split('\n')))
            alphaNums: [str] = list(
                filter(lambda p: match(r'[A-Za-z0-9]+\Z', p), parts))
            return str(alphaNums[0] if alphaNums != [] else str(
                max(parts, default=0, key=len)))

        if type(key) == str:
            ret = {'key': parse_name(key)}
        elif type(key) == dict:
            if nextKey is not None and type(nextKey) == str:
                ret = dict_union(key, {'key': parse_name(nextKey)})
                shift = 2
            else:
                ret = dict(key)
        else:
            die('Malformed data when reading %s and %s' %
                (str(key), str(layout)))

        if 'key-type' not in ret:
            ret_key: str = safe_get(ret, 'key')
            if safe_get(ret, 'x') == 0.25 \
                and safe_get(ret, 'a') == 7 \
                and safe_get(ret, 'w') == 1.25 \
                and safe_get(ret, 'h') == 2 \
                and safe_get(ret, 'w2') == 1.5 \
                and safe_get(ret, 'h2') == 1 \
                and safe_get(ret, 'x2') == -0.25:
                ret['key-type'] = 'iso-enter'
            elif ret_key == '+' and safe_get(ret, 'h') == 2:
                ret['key-type'] = 'num-plus'
            elif ret_key and ret_key.lower() == 'enter' and safe_get(ret,
                                                                     'h') == 2:
                ret['key-type'] = 'num-enter'
            elif ret_key and ret_key.lower() == 'caps lock' and safe_get(ret, 'w') == 1.25 and safe_get(ret, 'w2') == 1.75 and safe_get(ret, 'l') == True:
                ret['key-type'] = 'stepped-caps'

        if 'a' in ret:
            ret = rem(ret, 'a')

        if 'x' in ret:
            ret = key_subst(ret, 'x', 'shift-x')
        if 'y' in ret:
            ret = key_subst(ret, 'y', 'shift-y')
        if 'w' in ret:
            ret = key_subst(ret, 'w', 'width')
        else:
            ret['width'] = 1.0
        if 'h' in ret:
            ret = key_subst(ret, 'h', 'height')
        else:
            ret['height'] = 1.0

        if 'key' not in ret:
            printw("Key \"%s\" %s 'key' field, please put one in" %
                   (str(key), 'missing' if key != '' else 'has empty'))
            ret['key'] = 'SOME_ID@' + hex(id(key))

        return (shift, ret)

    if type(layout) != list and any(
            list(map(lambda l: type(l) != list, layout))):
        die('Expected a list of lists in the layout (see the JSON output of KLE)'
            )

    parsed_layout: [dict] = []
    row: float = 0.0
    lineInd: int = 0
    for line in layout:
        col: float = 0.0
        prevCol: float = 0.0
        i: int = 0
        while i < len(line):
            # Parse for the next key
            printi('Handling layout, looking at pair "%s" and "%s"' %
                   (str(line[i]).replace('\n', '\\n'),
                    str(safe_get(line, i + 1)).replace('\n', '\\n')))
            (shift, line[i]) = parse_key(line[i], safe_get(line, i + 1))
            key: dict = line[i]

            # Handle shifts
            if 'shift-y' in key:
                row += key['shift-y']
                col = 0
            if 'shift-x' in key:
                col += key['shift-x']

            # Apply current position data
            key['row'] = row
            key['col'] = col
            key['profile-part'] = layout_row_profiles[lineInd]

            # Add to layout
            if 'key' in key:
                parsed_layout += [key]

            # Move col to next position
            col += key['width']

            # Move to the next pair
            i += shift
        if len(line) > 1 and 'shift-y' not in line[-1]:
            row += 1
        lineInd = min([lineInd + 1, len(layout_row_profiles) - 1])

    return list(map(add_cap_name, parsed_layout))

def add_cap_name(key:dict) -> dict:
    key['cap-name'] = key['key-type'] if 'key-type' in key else (
        key ['profile-part'] + '-' +
        str(float(key ['width'])).replace('.', '_') + 'u') # I'm really hoping that python will behave reasonably w.r.t. floating point precision
    return key

