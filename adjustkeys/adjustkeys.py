#!/usr/bin/python3
# Copyright (C) Edward Jones

from .adjustcaps import adjust_caps, get_caps
from .adjustglyphs import adjust_glyphs, glyph_files
from .args import parse_args, Namespace
from .blender_available import blender_available
from .colour_map_parser import parse_colour_map
from .colour_resolver import colourise_layout
from .exceptions import AdjustKeysException, AdjustKeysGracefulExit
from .glyphinf import glyph_name
from .input_types import type_check_glyph_map, type_check_profile_data
from .layout import get_layout, dumb_parse_layout, compute_layout_dims
from .lazy_import import LazyImport
from .log import die, init_logging, printi, printw, print_warnings
from .scale import get_scale
from .update_checker import check_update
from .util import dict_union, safe_get
from .yaml_io import read_yaml
from os import makedirs
from os.path import exists, join
from sys import argv, exit
from yaml import dump
if blender_available():
    from bpy.types import Collection
    context = LazyImport('bpy', 'context')
Vector:type = LazyImport('mathutils', 'Vector')


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
                    dumb_parse_layout(read_yaml(pargs.layout_file))))))))
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

    # Read profile data
    profile_data:dict = {}
    if pargs.adjust_glyphs or pargs.adjust_caps:
        profile_data = read_yaml(join(pargs.cap_dir, 'profile_data.yml'))
        if not type_check_profile_data(profile_data):
            die('Profile data failed type-checking, see console for more information')

    # Read layout file
    layout:[dict] = []
    if pargs.adjust_glyphs or pargs.adjust_caps:
        layout:[dict] = get_layout(pargs.layout_file, profile_data, pargs.apply_colour_map)
    layout_dims:Vector = compute_layout_dims(layout)

    # Read colour-map file
    colour_map:[dict] = None
    if pargs.apply_colour_map:
        colour_map:[dict] = parse_colour_map(pargs.colour_map_file)

    coloured_layout:[dict] = colourise_layout(pargs.layout_file, layout, colour_map)

    glyph_map:dict = {}
    if pargs.adjust_glyphs:
        glyph_map = read_yaml(pargs.glyph_map_file)
        if not type_check_glyph_map(glyph_map):
            die('Glyph map failed type-checking see the console for more information')

    # Make collection
    collection:Collection = context.collection
    collection_data:dict = { 'temporary-collection': collection }

    # Adjust model positions
    model_data:dict = {}
    if pargs.adjust_caps:
        model_data = adjust_caps(coloured_layout, colour_map, profile_data, collection, layout_dims, pargs)

    glyph_data:dict = {}
    if pargs.glyph_application_method != 'uv-map' or pargs.adjust_caps:
        # Obtain data for glyph alignment
        model_name:str = safe_get(model_data, 'keycap-model-name')
        glyph_layout:[dict] = safe_get(model_data, '~caps-with-margin-offsets', default=coloured_layout)
        imgNode:ShaderNodeTexImage = safe_get(model_data, '~texture-image-node')
        uv_image_path:str = safe_get(model_data, 'uv-image-path')
        uv_material_name:str = safe_get(model_data, 'uv-material-name')

        # Adjust glyph positions
        glyph_data = adjust_glyphs(glyph_layout, profile_data, model_name, layout_dims, collection, glyph_map, imgNode, uv_image_path, uv_material_name, pargs)

    # Return info
    return remove_private_data(dict_union(collection_data, model_data, glyph_data))

def remove_private_data(d:dict) -> dict:
    return dict(filter(lambda p: not p[0].startswith('~'), d.items()))

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
