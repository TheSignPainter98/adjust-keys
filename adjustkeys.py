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

from adjustcaps import adjust_caps
from adjustglyphs import adjust_glyphs
from args import parse_args, Namespace
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

    if pargs.listKeys:
        print('\n'.join(
            list(
                map(
                    lambda k: k['key'],
                    parse_layout(read_yaml(pargs.layout_row_profile_file),
                                 read_yaml(pargs.layout_file))))))
        return 0
    if pargs.listGlyphs:
        print('\n'.join(
            list(
                map(lambda p: p[0],
                    read_yaml(pargs.glyph_offset_file).items()))))
        return 0

    if not exists(pargs.output_dir):
        printi('Making non-existent directory "%s"' % pargs.output_dir)
        makedirs(pargs.output_dir, exist_ok=True)

    layout:[dict] = get_layout(pargs.layout_file, pargs.layout_row_profile_file)

    model_name: str = adjust_caps(layout, pargs.cap_unit_length, pargs.cap_x_offset,
                                  pargs.cap_y_offset, pargs.cap_dir,
                                  pargs.output_dir, pargs.output_prefix, pargs.nprocs)
    glyphs_name: str = adjust_glyphs(layout,
        pargs.glyph_part_ignore_regex, pargs.profile_file,
        pargs.glyph_dir, pargs.glyph_map_file, pargs.glyph_unit_length, pargs.global_x_offset,
        pargs.global_y_offset, pargs.output_prefix, get_scale(pargs.cap_unit_length, pargs.glyph_unit_length))

    # If blender is loaded, shrink-wrap the glyphs onto the model
    if blender_available():
        shrink_wrap_glyphs_to_keys(glyphs_name, model_name, pargs.cap_unit_length, pargs.shrink_wrap_offset)

    return 0


if __name__ == '__main__':
    try:
        exit(main(argv))
    except KeyboardInterrupt:
        exit(1)
