# Copyright (C) Edward Jones

from .log import die, printi, printw
from .input_types import type_check_kle_layout
from .lazy_import import LazyImport
from .util import dict_union, key_subst, rem, safe_get
from .yaml_io import read_yaml
from math import cos, radians, sin
from types import SimpleNamespace
from re import match

Matrix:type = LazyImport('mathutils', 'Matrix')
Vector:type = LazyImport('mathutils', 'Vector')

cap_deactivation_colour:str = '#cccccc'
glyph_deactivation_colour:str = '#000000'

def get_layout(layout_file:str, profile_data:dict, use_deactivation_colour:bool) -> [dict]:
    return parse_layout(read_yaml(layout_file), profile_data, use_deactivation_colour)

def dumb_parse_layout(layout:[[dict]]) -> [dict]:
    return parse_layout(layout, None, True)

def parse_layout(layout: [[dict]], profile_data:dict, use_deactivation_colour:bool) -> [dict]:
    if not type_check_kle_layout(layout):
        die('KLE layout failed type-checking, see console for more information')
    printi('Reading layout information')

    if type(layout) != list and any(
            list(map(lambda l: type(l) != list, layout))):
        die('Expected a list of lists in the layout (see the JSON output of KLE)'
            )

    profile_row_map:dict = safe_get(profile_data, 'profile-row-map')

    parsed_layout: [dict] = []
    parser_default_state_dict:dict = {
            'c': cap_deactivation_colour if not use_deactivation_colour else None,
            't': glyph_deactivation_colour if not use_deactivation_colour else None,
            'i': 0,
            'x': 0.0,
            'y': 0.0,
            'r': 0.0,
            'rx': 0.0,
            'ry': 0.0,
            'p': profile_row_map['R1'] if profile_row_map is not None else 'R1',
        }
    parser_state:SimpleNamespace = SimpleNamespace(**parser_default_state_dict)
    for line in layout:
        parser_state.x = 0.0
        parser_state.i = 0
        if type(line) != list:
            continue
        while parser_state.i < len(line):
            # Parse for the next key
            printi('Handling layout, looking at pair "%s" and "%s"' %
                   (str(line[parser_state.i]).replace('\n', '\\n'),
                    str(safe_get(line, parser_state.i + 1)).replace('\n', '\\n')))
            (shift, line[parser_state.i]) = parse_key(line[parser_state.i], safe_get(line, parser_state.i + 1), parser_state, profile_row_map)
            key: dict = line[parser_state.i]

            # Handle colour changes
            parser_state.c = key['cap-style-raw']
            if use_deactivation_colour and parser_state.c == cap_deactivation_colour:
                parser_state.c = None
                key['cap-style-raw'] = None
            parser_state.t = key['glyph-colour-raw']
            if use_deactivation_colour and parser_state.t == glyph_deactivation_colour:
                parser_state.t = None
                key['glyph-colour-raw'] = None

            # Handle shifts
            if 'shift-y' in key:
                parser_state.y += key['shift-y']
                parser_state.x = 0.0
            if 'shift-x' in key:
                parser_state.x += key['shift-x']

            # Handle the profile
            parser_state.p = key['profile-part']

            # Handle the angle
            parser_state.r = key['rotation']
            if 'r' in key or 'rx' in key or 'ry' in key:
                if 'rx' in key:
                    parser_state.rx = key['rx']
                    key = rem(key, 'rx')
                else:
                    parser_state.rx = -key['shift-x'] if 'shift-x' in key else 0.0
                if 'ry' in key:
                    parser_state.ry = key['ry']
                    key = rem(key, 'ry')
                else:
                    parser_state.ry = -key['shift-y'] if 'shift-y' in key else 0.0
                parser_state.x = key['shift-x'] if 'shift-x' in key else 0.0
                parser_state.y = key['shift-y'] if 'shift-y' in key else 0.0

            # Apply current position data
            key['kle-pos'] = Vector((parser_state.rx, parser_state.ry)) + Matrix.Rotation(-parser_state.r, 2) @ Vector((parser_state.x, parser_state.y))

            # Add to layout
            if 'key' in key and (not 'd' in key or not key['d']):
                parsed_layout += [key]

            # Move col to next position
            parser_state.x += key['width']

            # Move to the keycap representation
            parser_state.i += shift
        if len(line) > 1 and 'shift-y' not in line[-1]:
            parser_state.y += 1

    return list(map(add_cap_name, parsed_layout))

def parse_key(key: 'either str dict', nextKey: 'maybe (either str dict)', parser_state:SimpleNamespace, profile_row_map:dict) -> [int, dict]:
    ret: dict
    shift: int = 1

    if type(key) == str:
        ret = {'key': parse_name(key)}
    elif type(key) == dict:
        if nextKey is not None and type(nextKey) == str:
            ret = dict_union(key, {'key': parse_name(nextKey)})
            shift = 2
        else:
            ret = dict(key)
    else:
        die('Malformed data when reading %s and %s' % (str(key), str(nextKey)))

    if 'key-type' not in ret:
        ret_key: str = safe_get(ret, 'key')
        x_in:float = safe_get(ret, 'x')
        if x_in is not None and x_in >= 0.25 \
            and safe_get(ret, 'w') == 1.25 \
            and safe_get(ret, 'h') == 2 \
            and safe_get(ret, 'w2') == 1.5 \
            and safe_get(ret, 'h2') == 1 \
            and safe_get(ret, 'x2') == -0.25:
            ret['key-type'] = 'iso-enter'
            ret['x'] -= 0.25
        elif ret_key.endswith('+') and safe_get(ret, 'h') == 2:
            ret['key-type'] = 'num-plus'
        elif ret_key and ret_key.lower().endswith('enter') and safe_get(ret,
                                                                 'h') == 2:
            ret['key-type'] = 'num-enter'

    if 'a' in ret:
        ret = rem(ret, 'a')

    if 'x' in ret:
        ret = key_subst(ret, 'x', 'shift-x')
    if 'y' in ret:
        ret = key_subst(ret, 'y', 'shift-y')
    if 'c' in ret:
        ret = key_subst(ret, 'c', 'cap-style-raw')
    else:
        ret['cap-style-raw'] = parser_state.c
    if 't' in ret:
        ret = key_subst(ret, 't', 'glyph-colour-raw')
    else:
        ret['glyph-colour-raw'] = parser_state.t
    if 'w' in ret:
        ret = key_subst(ret, 'w', 'width')
    else:
        ret['width'] = 1.0
    if 'w2' in ret:
        ret = key_subst(ret, 'w2', 'secondary-width')
    else:
        ret['secondary-width'] = ret['width']
    if 'h' in ret:
        ret = key_subst(ret, 'h', 'height')
    else:
        ret['height'] = 1.0
    if 'h2' in ret:
        ret = key_subst(ret, 'h2', 'secondary-height')
    else:
        ret['secondary-height'] = ret['height']
    if 'r' in ret:
        ret['r'] = radians(-ret['r'])
        ret['rotation'] = ret['r']
    else:
        ret['rotation'] = parser_state.r
    if 'n' in ret:
        ret = key_subst(ret, 'n', 'homing')
    else:
        ret['homing'] = False
    if 'l' in ret:
        ret = key_subst(ret, 'l', 'stepped')
    else:
        ret['stepped'] = False
    if 'p' in ret and ret['p']:
        if profile_row_map is not None:
            if ret['p'] in profile_row_map:
                ret['p'] = profile_row_map[ret['p']]
            else:
                printw('Profile row map does not contain key "%s" (this message appears once for each key which uses this profile)' % ret['p'])
        ret = key_subst(ret, 'p', 'profile-part')
    else:
        ret['profile-part'] = parser_state.p

    if 'key' not in ret:
        printw("Key \"%s\" %s 'key' field, please put one in" %
               (str(key), 'missing' if key != '' else 'has empty'))
        ret['key'] = 'SOME_ID@' + hex(id(key))

    return (shift, ret)


def parse_name(txt: str) -> str:
    return '-'.join(txt.split('\n'))


def add_cap_name(key:dict) -> dict:
    key['cap-name'] = gen_cap_name(key)
    return key

def gen_cap_name(key:dict) -> str:
    if 'key-type' in key:
        return key['key-type']
    else:
        name:str = '%s-%su' %(key['profile-part'], ('%.2f' % float(key['width'])).replace('.', '_'))
        if key['stepped']:
            name += '-%su' % ('%.2f' % float(key['secondary-height'])).replace('.', '_')
            name += '-%su' % ('%.2f' % float(key['secondary-width'])).replace('.', '_')
            name += '-stepped'
        if key['homing']:
            name += '-bar'
        return name

def compute_layout_dims(layout:[dict]) -> Vector:
    def point_enumerator(v:Vector) -> Matrix:
        return Matrix([
            (0.0, 0.0,  v[0], v[0]),
            (0.0, v[1], 0.0,  v[1])
        ])

    # Initial extreme values
    xmax = 0.0
    ymax = 0.0

    for cap in layout:
        rot:Matrix = Matrix.Rotation(-cap['rotation'], 2)
        primary_dims:Vector = Vector((cap['width'], cap['height']))
        secondary_dims:Vector = Vector((cap['secondary-width'], cap['secondary-height']))
        kle_pos_mat:Matrix = Matrix([[cap['kle-pos'][0]] * 4, [cap['kle-pos'][1]] * 4])

        # This method doesn't take into account extremely weird keycap shapes (which use x2, y2 keys but it should work for everything which actually exists)
        primary_points:Matrix = kle_pos_mat + rot @ point_enumerator(primary_dims)
        secondary_points:Matrix = kle_pos_mat + rot @ point_enumerator(secondary_dims)

        xmax = max(xmax, *primary_points[0], *secondary_points[0])
        ymax = max(ymax, *primary_points[1], *secondary_points[1])

    return Vector((xmax, ymax))
