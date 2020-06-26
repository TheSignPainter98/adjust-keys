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
# This was written on literally the hottest day of the year :(
# This was written the very next day, also on the hottest day of the year D:


from args import parse_args
from layout import parse_layout
from log import init_logging, printe, printi
from positions import resolve_positions
from sys import argv, exit
from yaml_io import read_yaml, write_yaml
from util import inner_join

##
# @brief Entry point function, should be treated as the first thing called
#
# @param args:[str] Command line arguments
#
# @return Zero if and only if the program is to exit successfully
def main(args:[str]) -> int:
    pargs = parse_args(args)
    init_logging(pargs.verbose, pargs.quiet)

    #  profile = read_yaml(pargs.profile_file)
    glyph_offsets = read_yaml(pargs.glyph_offset_file)
    glyph_offsets_rel = list(map(lambda m: { 'glyph': m[0], 'off-x': m[1]['x'] if 'x' in m[1] else 0.0, 'off-y': m[1]['y'] if 'y' in m[1] else 0.0 }, glyph_offsets.items()))
    layout:[dict] = parse_layout(read_yaml(pargs.layout_file))
    glyph_map = read_yaml(pargs.glyph_map_file)
    # Gee, a functor type class would really help here, you know? But that would require Python to have a decent type system and let's face it that'll probably never happen.
    glyph_rel = list(map(lambda m: { 'key': m[0], 'glyph': m[1] }, glyph_map.items()))

    key_offsets = inner_join(glyph_rel, 'glyph', glyph_offsets_rel, 'glyph')
    offset_layout = inner_join(key_offsets, 'key', layout, 'key')

    positions = resolve_positions(offset_layout, pargs.unit_length, pargs.delta_x, pargs.delta_y, pargs.global_x_offset, pargs.global_y_offset)

    write_yaml('-', positions)

    return 0

if __name__ == '__main__':
    exit(main(argv))
