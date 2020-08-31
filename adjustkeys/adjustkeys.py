#!/usr/bin/python3
# Copyright (C) Edward Jones

from .dependency_handler import handle_missing_dependencies
handle_missing_dependencies()

from .adjustcaps import adjust_caps, get_caps
from .adjustglyphs import adjust_glyphs, glyph_files
from .args import adjustkeys_path,parse_args, Namespace
from .blender_available import blender_available
from .exceptions import AdjustKeysException, AdjustKeysGracefulExit
from .glyphinf import glyph_name
from .layout import get_layout, parse_layout
from .log import die, init_logging, printi, printw, print_warnings
from .scale import get_scale
from .shrink_wrap import shrink_wrap_glyphs_to_keys
from .update_checker import update_available
from .util import dict_union
from .yaml_io import read_yaml
from os import makedirs
from os.path import exists, join
from sys import argv, exit
from yaml import dump


def main(*args:[[str]]) -> dict:
    try:
        return adjustkeys(args)
    except AdjustKeysGracefulExit:
        return 0
    finally:
        print_warnings()

def adjustkeys(*args: [[str]]) -> dict:
    pargs: Namespace = parse_args(args)
    init_logging(pargs.verbosity)

    if pargs.print_opts_yml:
        print(dump(pargs.__dict__)[:-1])
        return {}

    if update_available(pargs):
        printw('A new version is available, please download it by going to https://github.com/TheSignPainter98/adjust-keys/releases/latest. You can suppress update-checking with the -Vn or -Vs flags')
    if pargs.list_cap_names:
        print('\n'.join(
            list(sorted(set(
                map(
                    lambda k: k['key'],
                    parse_layout(read_yaml(pargs.layout_row_profile_file),
                                 read_yaml(pargs.layout_file), pargs.homing_keys)))))))
        return 0
    if pargs.list_glyphs:
        knownGlyphs:[[str,str]] = list(map(lambda g: [glyph_name(g), g], glyph_files(pargs.glyph_dir)))
        maxLen:int = max(map(lambda kg: len(kg[0]), knownGlyphs))
        for kg in knownGlyphs:
            kg[0] = kg[0].ljust(maxLen)
        print('\n'.join(list(map(lambda kg: ' @ '.join(kg), knownGlyphs))))
        return 0
    if pargs.list_cap_models:
        knownCaps:[[str,str]] = list(map(lambda c: [c['cap-name'], c['cap-source']], get_caps(pargs.cap_dir)))
        maxLen:int = max(map(lambda kc: len(kc[0]), knownCaps))
        for kc in knownCaps:
            kc[0] = kc[0].ljust(maxLen)
        print('\n'.join(list(map(lambda kc: kc[0] + ' @ ' + kc[1], knownCaps))))
        return 0

    layout:[dict] = get_layout(pargs.layout_file, pargs.layout_row_profile_file, pargs.homing_keys)

    if not blender_available():
        die('bpy is not available, please run `adjustkeys` from within Blender (instructions should be in the supplied README.md file)')

    if not exists(pargs.output_dir):
        printi('Making non-existent directory "%s"' % pargs.output_dir)
        makedirs(pargs.output_dir, exist_ok=True)

    # Adjust model positions
    model_data:dict = {}
    if not pargs.no_adjust_caps:
        model_data = adjust_caps(layout, pargs)

    # Adjust glyph positions
    glyph_data:dict = {}
    if not pargs.no_adjust_glyphs:
        glyph_data = adjust_glyphs(layout, pargs)

    # If blender is loaded, shrink-wrap the glyphs onto the model
    if not pargs.no_shrink_wrap and not pargs.no_adjust_caps and not pargs.no_adjust_glyphs:
        shrink_wrap_glyphs_to_keys(glyph_data['glyph-names'], model_data['keycap-model-name'], pargs.cap_unit_length, pargs.shrink_wrap_offset)

    return dict_union(model_data, glyph_data)

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
