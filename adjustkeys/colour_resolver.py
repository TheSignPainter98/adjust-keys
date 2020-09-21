# Copyright (C) Edward Jones

from re import IGNORECASE, match

def colourise_layout(layout:[dict], colour_map:[dict]) -> [dict]:
    for key in layout:
        apply_sanitised_colouring(key, colour_map, 'cap-colour', 'cap-colour-raw', 'name')
        apply_sanitised_colouring(key, colour_map, 'glyph-style', 'glyph-colour-raw', 'glyph-style')
    return layout

def apply_sanitised_colouring(key:dict, colour_map:[dict], target_key:str, raw_key:str, extraction_key:str):
    key[target_key] = sanitise_colour(get_colouring(key, colour_map, target_key, raw_key, extraction_key))

def get_colouring(key:dict, colour_map:[dict], target_key:str, raw_key:str, extraction_key:str) -> str:
    if raw_key in key and key[raw_key] is not None:
        return key[raw_key]
    else:
        if colour_map is not None:
            key_name = key['key']
            for mapping in colour_map:
                if target_key in mapping and any(map(lambda r: match('^' + r + '$', key_name, IGNORECASE) is not None, mapping['keys'])):
                    return mapping[extraction_key]
        return None

def sanitise_colour(colour_str:str) -> str:
    if colour_str is None:
        return None

    if colour_str[0] == '#':
        colour_str = colour_str[1:]
    return colour_str
