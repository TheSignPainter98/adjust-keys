# Copyright (C) Edward Jones

from .log import printi
from functools import partial
from mathutils import Matrix, Vector
from os import sep
from os.path import basename, split, splitext
from re import IGNORECASE, match, UNICODE
from typing import Callable, List, Tuple, Union

def colourise_layout(layout_file_path:str, layout:[dict], colour_map:[dict]) -> [dict]:
    layout_context:dict = {
            'layout-file-path': sanitise_path(layout_file_path),
            'layout-file-name': splitext(basename(layout_file_path))[0],
        }
    for key in layout:
        apply_sanitised_colouring(layout_context, key, colour_map, 'cap-style', 'cap-style-raw', 'cap-style')
        apply_sanitised_colouring(layout_context, key, colour_map, 'glyph-style', 'glyph-colour-raw', 'glyph-style')
    return layout

def sanitise_path(path:str) -> str:
    folders = []
    while True:
        path, folder = split(path)
        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)
            break
    folders.reverse()
    return '/'.join(folders)

def apply_sanitised_colouring(layout_context:dict, key:dict, colour_map:[dict], target_key:str, raw_key:str, extraction_key:str):
    (key[target_key], key[target_key + '-rule']) = sanitise_colour(get_colouring(layout_context, key, colour_map, target_key, raw_key, extraction_key))

def get_colouring(layout_context:dict, key:dict, colour_map:[dict], target_key:str, raw_key:str, extraction_key:str) -> Tuple[str, str]:
    if raw_key in key and key[raw_key] is not None:
        return (key[raw_key], None)
    else:
        if colour_map is not None:
            for mapping in colour_map:
                if target_key in mapping and rule_match(layout_context, key, mapping):
                    return (mapping[extraction_key], mapping['name'])
        return (None, None)

def rule_match(layout_context:dict, key:dict, rule:dict) -> bool:
    return all(resolve_matches(layout_context, key, rule['cond']))
    #  key_name:str = key['key']
    #  return any(map(lambda r: match('^' + r + '$', key_name, IGNORECASE) is not None, rule['keys']))

def resolve_matches(layout_context:dict, cap:dict, rule:Union[bool, dict]) -> [bool]:
    if type(rule) == bool:
        return [rule]

    printi_name:Callable = partial(printi, '%s:' % layout_context['layout-file-name'])
    conds:[bool] = []

    # Resolve conditions at this level
    for statementKey in rule:
        if statementKey.startswith('key-name'):
            printi_name('Checking key name "%s" entirely matches any of' % cap['key'], end=' ')
            key_name_regexes = rule['key-name'] if type(rule['key-name']) == list else [rule['key-name']]
            printi('[ %s ]...' % ', '.join(list(map(lambda r: '"%s"' % r, key_name_regexes))), end=' ')
            cond_result:bool = any(map(lambda r: match('^%s$' % r, cap['key'], IGNORECASE | UNICODE) is not None, key_name_regexes))
            printi('%r' % cond_result)

            conds.append(cond_result)
        if statementKey.startswith('key-pos'):
            printi_name('Checking key position (%.4fu,%.4fu) satisfies condition "%s"...' % (cap['kle-pos'].x, cap['kle-pos'].y, rule['key-pos']), end=' ')
            print(rule)
            cond_result:bool = eval_maths_cond(cap, rule['parsed-key-pos'])
            printi('%r' % cond_result)

            conds.append(cond_result)
        if statementKey.startswith('layout-file-name'):
            printi_name('Checking "%s" entirely matches "%s"...' % (layout_context['layout-file-name'], rule['layout-file-name']), end=' ')
            cond_result:bool = match('^%s$' % rule['layout-file-name'], layout_context['layout-file-name'], IGNORECASE | UNICODE) is not None
            printi('%r' % cond_result)

            conds.append(cond_result)
        if statementKey.startswith('layout-file-path'):
            printi_name('Checking "%s" entirely matches "%s"...' % (layout_context['layout-file-path'], rule['layout-file-path']), end=' ')
            cond_result:bool = match('^%s$' % rule['layout-file-path'], layout_context['layout-file-path'], IGNORECASE | UNICODE) is not None
            printi('%r' % cond_result)

            conds.append(cond_result)

        # Resolve sub-conditions
        if statementKey.startswith('any'):
            conds.append(any(resolve_matches(layout_context, cap, rule[statementKey])))
        if statementKey.startswith('all'):
            conds.append(all(resolve_matches(layout_context, cap, rule[statementKey])))
        if statementKey.startswith('not-all'):
            conds.append(not all(resolve_matches(layout_context, cap, rule[statementKey])))
        if statementKey.startswith('not-any'):
            conds.append(not any(resolve_matches(layout_context, cap, rule[statementKey])))

    return conds

def eval_maths_cond(cap:dict, pos_cond:Union[str, int, float, dict]) -> object:
    if type(pos_cond) in [int, float]:
        return pos_cond
    elif type(pos_cond) == str:
        return {
            'x': lambda: cap['kle-pos'].x,
            'y': lambda: cap['kle-pos'].y,
            'X': lambda: (cap['kle-pos'] + 0.5 * Matrix.Rotation(cap['rotation'], 2) @ Vector((cap['secondary-width'], cap['secondary-height']))).x,
            'Y': lambda: (cap['kle-pos'] + 0.5 * Matrix.Rotation(cap['rotation'], 2) @ Vector((cap['secondary-width'], cap['secondary-height']))).y,
        }[pos_cond]()
    elif type(pos_cond) == dict:
        eval_cap_cond:Callable = partial(eval_maths_cond, cap)
        return pos_cond['op'](*tuple(map(eval_cap_cond, pos_cond['args'])))

def sanitise_colour(colour_str:str) -> str:
    if colour_str is None:
        return None

    if colour_str[0] == '#':
        colour_str = colour_str[1:]
    return colour_str
