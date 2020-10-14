#!/usr/bin/python3
# Copyright (C) Edward Jones

from .adjustcaps import adjust_caps, get_caps
from .adjustglyphs import adjust_glyphs, glyph_files
from .args import parse_args, Namespace
from .blender_available import blender_available
from .colour_resolver import colourise_layout
from .collections import make_collection
from .exceptions import AdjustKeysException, AdjustKeysGracefulExit
from .glyphinf import glyph_name
from .input_types import type_check_colour_map, type_check_glyph_map, type_check_profile_data
from .layout import get_layout, parse_layout
from .log import die, init_logging, printi, printw, print_warnings
from .scale import get_scale
from .shrink_wrap import shrink_wrap_glyphs_to_keys
from .update_checker import check_update
from .util import dict_union
from .yaml_io import read_yaml
from os import makedirs
from os.path import exists, join
from sys import argv, exit
from yaml import dump
if blender_available():
    from bpy.types import Collection


def main(*args:[[str]]) -> dict:
    ret:dict = {}
    try:
        ret = adjustkeys(args)
    except AdjustKeysGracefulExit:
        ret = {}
    finally:
        num_warnings:int = print_warnings()
        ret['num_warnings'] = num_warnings
    return ret

def adjustkeys(*args: [[str]]) -> dict:
    pargs: Namespace = parse_args(args)
    init_logging(pargs)

    if pargs.print_opts_yml:
        print(dump(pargs.__dict__)[:-1])
        return {}

    if pargs.check_update:
        if check_update():
            print('A new version is available, please download it by going to https://github.com/TheSignPainter98/adjust-keys/releases/latest')
        else:
            print('Adjustkeys is up-to-date.')
        return {}
    if pargs.list_cap_names:
        print('\n'.join(
            list(sorted(set(
                map(
                    lambda k: k['key'],
                    get_layout(pargs.layout_file, not pargs.no_apply_colour_map)))))))
        return {}
    if pargs.list_glyphs:
        knownGlyphs:[[str,str]] = list(map(lambda g: [glyph_name(g), g], glyph_files(pargs.glyph_dir)))
        maxLen:int = max(map(lambda kg: len(kg[0]), knownGlyphs))
        for kg in knownGlyphs:
            kg[0] = kg[0].ljust(maxLen)
        print('\n'.join(list(map(lambda kg: ' @ '.join(kg), knownGlyphs))))
        return {}
    if pargs.list_cap_models:
        knownCaps:[[str,str]] = list(map(lambda c: [c['cap-name'], c['cap-source']], get_caps(pargs.cap_dir)))
        maxLen:int = max(map(lambda kc: len(kc[0]), knownCaps))
        for kc in knownCaps:
            kc[0] = kc[0].ljust(maxLen)
        print('\n'.join(list(map(lambda kc: kc[0] + ' @ ' + kc[1], knownCaps))))
        return {}

    if not blender_available():
        die('bpy is not available, please run `adjustkeys` from within Blender (instructions should be in the supplied README.md file)')

    profile_data:dict
    if not pargs.no_adjust_glyphs and not pargs.no_adjust_caps:
        profile_data = read_yaml(join(pargs.cap_dir, 'profile_data.yml'))
        if not type_check_profile_data(profile_data):
            die('Profile data failed type-checking, see console for more information')

    layout:[dict] = []
    if not pargs.no_adjust_glyphs and not pargs.no_adjust_caps:
        layout:[dict] = get_layout(pargs.layout_file, profile_data, not pargs.no_apply_colour_map)
    colour_map:[dict] = []

    colour_map:[dict]
    if not pargs.no_adjust_glyphs and not pargs.no_adjust_caps:
        colour_map = read_yaml(pargs.colour_map_file) if not pargs.no_apply_colour_map else None
        if not type_check_colour_map(colour_map):
            die('Colour map failed type-checking, see console for more information')

    coloured_layout:[dict] = colourise_layout(layout, colour_map)

    glyph_map:dict
    if not pargs.no_adjust_glyphs:
        glyph_map = read_yaml(pargs.glyph_map_file)
        if not type_check_glyph_map(glyph_map):
            die('Glyph map failed type-checking see the console for more information')

    # Make the collection
    collection:Collection = make_collection('adjustkeys_caps_and_glyphs')
    collection_data:dict = { 'containing_collection': collection }

    # Adjust model positions
    model_data:dict = {}
    if not pargs.no_adjust_caps:
        model_data = adjust_caps(layout, colour_map, profile_data, collection, pargs)

    # Adjust glyph positions
    glyph_data:dict = {}
    if not pargs.no_adjust_glyphs:
        glyph_data = adjust_glyphs(layout, profile_data, collection, glyph_map, pargs)

    # If blender is loaded, shrink-wrap the glyphs onto the model
    if not pargs.no_shrink_wrap and not pargs.no_adjust_caps and not pargs.no_adjust_glyphs:
        shrink_wrap_glyphs_to_keys(glyph_data['glyph-names'], model_data['keycap-model-name'], profile_data['unit-length'], pargs.shrink_wrap_offset, profile_data['scale'] * pargs.scaling)

    return dict_union(collection_data, model_data, glyph_data)

if __name__ == '__main__':
    rc:int = 0
    err:Exception = None
    try:
        rc = adjustkeys(argv) is None
    except KeyboardInterrupt:
        rc = 1
    except AdjustKeysGracefulExit:
        rc = 0
    except AdjustKeysException as akex:
        print(argv[0] + ':', akex)
        rc = 1
    exit(rc)
