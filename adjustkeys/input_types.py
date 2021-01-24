# Copyright (C) Edward Jones

from .log import printe
from .util import list_diff
from re import IGNORECASE, match

# The equivalent Haskell code to do all this would add a total of zero extra lines to the existing program. Thanks Python, get a type system.

def type_check_profile_data(pd:object) -> bool:
    okay:bool = True
    t:bool
    (okay, t) = assert_type(okay, pd, dict, 'Expected a dictionary in the profile data')
    if not t:
        return False

    # unit_length
    (okay, t) = assert_dict_key(okay, pd, 'unit-length', 'Profile data has no unit-length key')
    if t:
        assert_type(okay, pd['unit-length'], float, 'Unit length should be a number with a decimal point')

    # scale
    (okay, t) = assert_dict_key(okay, pd, 'scale', 'Profile data has no scale key')
    if t:
        assert_type(okay, pd['scale'], float, 'Scale should be a number with a decimal point')

    # y-offsets
    (okay, t) = assert_dict_key(okay, pd, 'y-offsets', 'Profile data has no y-offsets key')
    if t:
        (okay, t) = assert_type(okay, pd, dict, 'y-offsets should be a dictionary')
        if t:
            for k,v in pd['y-offsets'].items():
                (okay, _) = assert_type(okay, v, float, 'y-offset for %s should be a number with a decimal point' % k)

    # special-offsets
    (okay, t) = assert_dict_key(okay, pd, 'special-offsets', 'Profile data missing special-offsets key')
    if t:
        (okay, t) = assert_type(okay, pd['special-offsets'], dict, 'Special offsets should be a dictionary')
        if t:
            (okay, t) = assert_cond(okay, set(pd['special-offsets'].keys()) == { 'iso-enter', 'num-enter', 'num-plus' }, 'Special offset keys must be exactly the set %s' % str(['iso-enter', 'num-enter', 'num-plus']))
            if not t:
                extra_keys:[str] = list_diff(pd['special-offsets'].keys(), ['iso-enter', 'num-enter', 'num-plus'])
                missing_keys:[str]  = list_diff(['iso-enter', 'num-enter', 'num-plus'], pd['special-offsets'].keys())
                if extra_keys != []:
                    print('Got unexpected special offset keys, expected %s but got: \n\t%s' % (str(['iso-enter', 'num-enter', 'num-plus']), '\n\t'.join(extra_keys)))
                if missing_keys != []:
                    print('Missing special offset keys: \n\t%s' % '\n\t'.join(missing_keys))
            for k,v in pd['special-offsets'].items():
                (okay, _) = assert_type(okay, v, float, 'Special offset for %s must be a number with a deciml point' % k)
    return okay

def type_check_kle_layout(kl:object) -> [[bool, bool]]:
    okay:bool = True
    t:bool
    (okay, t) = assert_type(okay, kl, list, 'KLE layout should be list at the outermost level')
    if not okay:
        return False

    for line in kl:
        (okay, t) = assert_cond(okay, type(kl) in [dict, list], 'An item in the outermost list of the KLE file is not a dictionary or a list')
        if t:
            if type(line) == list:
                for keypart in line:
                    if type(keypart) != str:
                        (okay, t) = assert_type(okay, keypart, dict, 'The innermost lists of a KLE file must contain only strings and mappings')
                        if t:
                            for k,v in keypart.items():
                                if k in ['c', 't']:
                                    (okay, _) = assert_cond(okay, match(r'^#[a-f0-9]$', v, IGNORECASE), 'Key %s must have values of the form: "#" + a six-digit hex value, got %s' %(k, str(v)))
                                elif k in ['l', 'n', 'd', 'g']:
                                    (okay, _) = assert_type(okay, v, bool, 'Key %s must be either true/false, for %s' %(k, str(v)))
                                elif k == 'p':
                                    (okay, _) = assert_cond(okay, v in ['R1', 'R2', 'R3', 'R4', 'R5', 'SPACE', '', None], 'Adjustkeys only recognises profiles R1-5 and SPACE, got value %s for p-key' % str(v))
                                else:
                                    (okay, _) = assert_cond(okay, type(v) in [float, int], 'Expected either an integer, or a number with a decimal point for key %s, got %s' %(k, str(v)))
    return okay

def type_check_glyph_map(gm:object) -> [[bool, bool]]:
    okay:bool = True
    t:bool
    (okay, t) = assert_type(okay, gm, dict, 'A glyph map is a dictionary')
    if not t:
        return False
    for k,v in gm.items():
        (okay, _) = assert_type(okay, k, str, 'Glyph map keys should be strings, got %s' % str(k))
        (okay, _) = assert_type(okay, k, str, 'Glyph map values should be strings, got %s' % str(v))

    return okay

def type_check_colour_map(cm:object) -> [[bool, bool]]:
    okay:bool = True
    t:bool
    (okay, t) = assert_type(okay, cm, list, 'A valid colour map consists of a list of rules, got a %s' % str(type(cm)))
    if not t:
        return False

    for rule in cm:
        (okay, t) = assert_type(okay, rule, dict, 'Colour-map rules should be dictionaries, got a %s' % str(type(rule)))
        if t:
            (okay, t) = assert_dict_key(okay, rule, 'name', 'Colour-map rule missing "name" field')
            if t:
                (okay, _) = assert_type(okay, rule['name'], str, 'Colour-map rule names should be strings, got "%s"' % str(rule['name']))
            (okay, t) = assert_dict_key(okay, rule, 'cond', 'Colour-map rules require a condition they should apply to')
            if t:
                okay = type_check_cond(okay, rule['cond'])
            if 'cap-style' in rule:
                (okay, _) = assert_type(okay, rule['cap-style'], str, 'Cap-styles should be strings, got %s' % (str(rule['cap-style'])))
            if 'glyph-style' in rule:
                (okay, _) = assert_type(okay, rule['glyph-style'], str, 'Glyph-styles should be strings (of either a single hex colour or CSS fragment), got %s' % rule['glyph-style'])

    return okay

def type_check_cond(p:bool, rule:dict) -> bool:
    conditions:dict = {
        'key-name': lambda p: assert_cond(p, type(rule['key-name']) == str or (type(rule['key-name']) == list and all(map(lambda k: type(k) in [str, int], rule['key-name']))), 'key-name field should be either a single key or list of keys, got "%s"' %(', '.join(rule['key-name']) if isinstance(rule['key-name'], list) else rule['key-name'])),
        'key-pos': lambda p: assert_type(p, rule['key-pos'], str, 'key-pos field takes an expression, got %s' % rule['key-pos']),
        'layout-file-name': lambda p: assert_type(p, rule['layout-file-name'], str, 'Layout-file-name field should be a string, got %s' % rule['layout-file-name']),
        'layout-file-path': lambda p: assert_type(p, rule['layout-file-path'], str, 'Layout-file-path field should be a string, got %s' % rule['layout-file-path']),
        'all': lambda p: (type_check_cond(p, rule['all']), None),
        'any': lambda p: (type_check_cond(p, rule['any']), None),
        'not-all': lambda p: (type_check_cond(p, rule['not-all']), None),
        'not-any': lambda p: (type_check_cond(p, rule['not-any']), None),
    }
    (p, _) = assert_cond(p, any(map(lambda k: k in rule, conditions.keys())), 'Rule needs at least one of: %s' % ', '.join(list(conditions.keys())))

    for field in rule.keys():
        if field not in conditions:
            printe('Unrecognised colour map rule field %s, is this a typo?' % field)
            p = False
        else:
            (p, _) = conditions[field](p)

    return p

def assert_type(p:bool, o:object, t:type, s:str) -> [[bool, bool]]:
    return assert_cond(p, type(o) == t, s)

def assert_dict_key(p:bool, o:dict, k:str, s:str) -> [[bool, bool]]:
    return assert_cond(p, k in o, s)

def assert_dict_keys(p:bool, o:dict, ks:[str], s:str) -> [[bool, bool]]:
    t:bool = True
    for k in ks:
        if k not in o:
            printe(s % k)
            t = False
    return (p, t)

def assert_cond(p:bool, c:bool, s:str) -> [[bool, bool]]:
    if not c:
        printe(s)
    return (p & c, c)
