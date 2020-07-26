#!/usr/bin/python3
# Copyright (C) Edward Jones
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

from blender_available import blender_available
if blender_available():
    from bpy import ops

from adjustcaps import adjust_caps, get_caps
from adjustglyphs import adjust_glyphs, glyph_files
from args import parse_args, Namespace
from glyphinf import glyph_name
from layout import get_layout, parse_layout
from log import init_logging, printi
from os import makedirs
from os.path import exists
from scale import get_scale
from shrink_wrap import shrink_wrap_glyphs_to_keys
from sys import argv, exit
from yaml_io import read_yaml


def main(*args: [[str]]) -> int:
    pargs: Namespace = parse_args(args)
    init_logging(pargs.verbosity)

    if pargs.list_cap_names:
        print('\n'.join(
            list(sorted(set(
                map(
                    lambda k: k['key'],
                    parse_layout(read_yaml(pargs.layout_row_profile_file),
                                 read_yaml(pargs.layout_file))))))))
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


    if not exists(pargs.output_dir):
        printi('Making non-existent directory "%s"' % pargs.output_dir)
        makedirs(pargs.output_dir, exist_ok=True)

    layout:[dict] = get_layout(pargs.layout_file, pargs.layout_row_profile_file)

    # Adjust model positions
    model_name:str
    if not pargs.no_adjust_caps:
        model_name = adjust_caps(layout, pargs.cap_unit_length, pargs.cap_x_offset,
                                      pargs.cap_y_offset, pargs.cap_dir,
                                      pargs.output_dir, pargs.output_prefix, pargs.nprocs)

    # Adjust glyph positions
    glyph_names:[str]
    if not pargs.no_adjust_glyphs:
        glyph_names = adjust_glyphs(layout,
            pargs.glyph_part_ignore_regex, pargs.profile_file,
            pargs.glyph_dir, pargs.glyph_map_file, pargs.glyph_unit_length, pargs.global_x_offset,
            pargs.global_y_offset, pargs.output_prefix, get_scale(pargs.cap_unit_length, pargs.glyph_unit_length, pargs.svg_units_per_mm))

    # If blender is loaded, shrink-wrap the glyphs onto the model
    if not pargs.no_shrink_wrap and not pargs.no_adjust_caps and not pargs.no_adjust_glyphs and blender_available():
        shrink_wrap_glyphs_to_keys(glyph_names, model_name, pargs.cap_unit_length, pargs.shrink_wrap_offset)

    return 0


if __name__ == '__main__':
    try:
        exit(main(argv))
    except KeyboardInterrupt:
        exit(1)
