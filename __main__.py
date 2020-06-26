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

from args import parse_args, Namespace
from layout import parse_layout
from log import die, init_logging, printe, printi
from positions import resolve_positions
from sys import argv, exit
from yaml_io import read_yaml, write_yaml
from util import dict_union, inner_join, rob_rem


##
# @brief Entry point function, should be treated as the first thing called
#
# @param args:[str] Command line arguments
#
# @return Zero if and only if the program is to exit successfully
def main(args: [str]) -> int:
    pargs = parse_args(args)
    init_logging(pargs.verbose, pargs.quiet)

    data = collect_data(pargs)

    positions = resolve_positions(data, pargs.unit_length, pargs.delta_x,
                                  pargs.delta_y, pargs.global_x_offset,
                                  pargs.global_y_offset)

    write_yaml('-', positions)

    return 0


def collect_data(pargs: Namespace) -> [dict]:
    profile: dict = read_yaml(pargs.profile_file)
    profile_x_offsets_rel: [dict] = list(
        map(lambda m: {
            'width': m[0],
            'p-off-x': m[1]
        }, profile['x-offsets'].items()))
    profile_y_offsets_rel: [dict] = list(
        map(lambda m: {
            'profile-part': m[0],
            'p-off-y': m[1]
        }, profile['y-offsets'].items()))
    profile_special_offsets_rel: [dict] = list(
        map(
            lambda m: {
                'key-type': m[0],
                'p-off-x': m[1]['x'] if 'x' in m[1] else 0.0,
                'p-off-y': m[1]['y'] if 'y' in m[1] else 0.0
            }, profile['special-offsets'].items()))
    layout_row_profiles: [str] = read_yaml(pargs.layout_row_profile_file)
    glyph_offsets = read_yaml(pargs.glyph_offset_file)
    glyph_offsets_rel = list(
        map(
            lambda m: dict_union({
                'glyph': m[0],
                'off-x': m[1]['x'] if 'x' in m[1] else 0.0,
                'off-y': m[1]['y'] if 'y' in m[1] else 0.0,
            }, rob_rem(rob_rem(m[1], 'x'), 'y')), glyph_offsets.items()))
    layout: [dict] = parse_layout(layout_row_profiles,
                                  read_yaml(pargs.layout_file))
    glyph_map = read_yaml(pargs.glyph_map_file)
    # Gee, a functor type class would really help here, you know? But that would require Python to have a decent type system and let's face it that'll probably never happen.
    glyph_rel = list(
        map(lambda m: {
            'key': m[0],
            'glyph': m[1]
        }, glyph_map.items()))

    key_offsets = inner_join(glyph_rel, 'glyph', glyph_offsets_rel, 'glyph')
    glyph_offset_layout = inner_join(key_offsets, 'key', layout, 'key')
    profile_x_offset_keys = inner_join(glyph_offset_layout, 'width',
                                       profile_x_offsets_rel, 'width')
    profile_x_y_offset_keys = inner_join(profile_x_offset_keys, 'profile-part',
                                         profile_y_offsets_rel, 'profile-part')
    data = list(map(lambda k: k if 'key-type' not in k else dict_union(k, list(filter(lambda s: s['key-type'] == k['key-type'], profile_special_offsets_rel))[0]), profile_x_y_offset_keys))

    return data


if __name__ == '__main__':
    exit(main(argv))
