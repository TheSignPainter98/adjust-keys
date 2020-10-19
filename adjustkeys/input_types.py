# Copyright (C) Edward Jones

from .log import printe
from re import IGNORECASE, match

# The equivalent Haskell code to do all this would add a total of zero extra lines to the existing program. Thanks Python, get a type system.

def type_check_profile_data(pd:object) -> bool:
    okay:bool = True
    t:bool
    (okay, t) = assert_type(okay, pd, dict, 'Expected a dictionary in the profile data')
    if not t:
        return False

    # margin-offset
    (okay, t) = assert_dict_key(okay, pd, 'margin-offset', 'Profile data has no margin-offset key')
    if t:
        assert_type(okay, pd['margin-offset'], float, 'Margin offset should be a number with a decimal point')

    # unit_length
    (okay, t) = assert_dict_key(okay, pd, 'unit-length', 'Profile data has no unit-length key')
    if t:
        assert_type(okay, pd['unit-length'], float, 'Unit length should be a number with a decimal point')

    # scale
    (okay, t) = assert_dict_key(okay, pd, 'scale', 'Profile data has no scale key')
    if t:
        assert_type(okay, pd['scale'], float, 'Scale should be a number with a decimal point')

    # x-offsets
    (okay, t) = assert_dict_key(okay, pd, 'x-offsets', 'Profile data has no x-offsets key')
    if t:
        (okay, t) = assert_type(okay, pd['x-offsets'], dict, 'Profile data x-offsets should be a mapping')
        if t:
            for k,v in pd['x-offsets'].items():
                (okay, _) = assert_type(okay, v, float, 'x-offset for %s should be a number with a decimal point' % k)

    # y-offsets
    (okay, t) = assert_dict_key(okay, pd, 'y-offsets', 'Profile data has no y-offsets key')
    if t:
        for k,v in pd['y-offsets'].items():
            (okay, _) = assert_type(okay, v, float, 'y-offset for %s should be a number with a decimal point' % k)

    # special-offsets
    (okay, t) = assert_dict_key(okay, pd, 'special-offsets', 'Profile data missing special-offsets key')
    if t:
        (okay, t) = assert_type(okay, pd['special-offsets'], dict, 'Special offsets should be a dictionary')
        if t:
            for rkey in ['iso-enter', 'num-enter', 'num-plus']:
                (okay, _) = assert_dict_key(okay, pd['special-offsets'], rkey, 'Special offsets is missing %s key' % rkey)
            if 'iso-enter' in pd['special-offsets']:
                for k in ['top-left', 'top-centre', 'top-right', 'middle-centre', 'middle-right', 'bottom-centre', 'bottom-right']:
                    (okay, _) = assert_dict_key(okay, pd['special-offsets']['iso-enter'], k, 'Special offsets for iso-enter is missing key %s' % k)
            for k,v in pd['special-offsets'].items():
                (okay, t) = assert_type(okay, v, dict, 'Special offset for %s must be a dictionary' % k)
                if t:
                    if k == 'iso-enter':
                        (okay, t) = assert_type(okay, v, dict, 'iso-enter special offsets should be a dictionary')
                        if t:
                            for k2,v2 in v.items():
                                (okay, t) = assert_type(okay, v2, dict, 'Iso-enter special offset for %s should be a dictionary' % k2)
                                if t:
                                    (okay, t) = assert_dict_key(okay, v2, 'x', 'Iso-enter special offset %s is missing x key' % k2)
                                    if t:
                                        (okay, _) = assert_type(okay, v2['x'], float, 'Iso-enter special offset %s\'s x key should be a number with a decimal point' % k2)
                                    (okay, t) = assert_dict_key(okay, v2, 'y', 'Iso-enter special offset %s is missing y key' % k2)
                                    if t:
                                        (okay, _) = assert_type(okay, v2['y'], float, 'Iso-enter special offset %s\'s y key should be a number with a decimal point' % k2)
                    else:
                        (okay, t) = assert_dict_key(okay, v, 'y', 'Special offset %s is missing a y-value' % k)
                        if t:
                            (okay, _) = assert_type(okay, v['y'], float, 'special y-offset for %s\'s should be a number with a decimal point' % k)
                        if 'x' in v:
                            (okay, _) = assert_type(okay, v['x'], float, 'special x-offset for %s\'s should be a number with a decimal point' % k)
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
            (okay, t) = assert_dict_key(okay, rule, 'keys', 'Colour-map rules require a list of keys they apply to')
            if t:
                (okay, t) = assert_type(okay, rule['keys'], list, 'Colour-map rule keys must be a list')
                if t:
                    for key in rule['keys']:
                        (okay, _) = assert_type(okay, key, str, 'Colour-map rule keys must be strings, got %s' % str(key))
            if 'cap-colour' in rule:
                (okay, _) = assert_type(okay, rule['cap-colour'], str, 'Cap-colours should be strings, got %s' % rule['cap-colour'])
            if 'glyph-style' in rule:
                (okay, _) = assert_type(okay, rule['glyph-style'], str, 'Glyph-styles should be strings (of either a single hex colour or CSS fragment), got %s' % rule['glyph-style'])

    return okay

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
