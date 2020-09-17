# Copyright (C) Edward Jones

from re import IGNORECASE, match

def colourise_layout(layout:[dict], colour_map:[dict]) -> [dict]:
    for key in layout:
        apply_colouring(key, colour_map, 'cap-colour', 'cap-colour-raw')
        apply_colouring(key, colour_map, 'glyph-style', 'glyph-colour-raw')
    return layout

def apply_colouring(key:dict, colour_map:[dict], target_key:str, raw_key:str):
    if raw_key in key:
        key[target_key] = key[raw_key]
    else:
        if colour_map is not None:
            key_name = key['key']
            for mapping in colour_map:
                if any(map(lambda r: match('^' + r + '$', key_name, IGNORECASE) is not None, mapping['keys'])):
                    key[target_key] = mapping['name']
                    return
        key[target_key] = None
