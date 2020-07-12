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

from adjustkeys import adjust_keys
from args import parse_args, Namespace
from layout import parse_layout
from sys import argv, exit
from util import concat
from yaml_io import read_yaml, write_yaml


##
# @brief Entry point function, should be treated as the first thing called
#
# @param args:[str] Command line arguments
#
# @return Zero if and only if the program is to exit successfully
def main(args: [str]) -> int:
    pargs: Namespace = parse_args(args)

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

    svg: str = adjust_keys(pargs.verbosity, pargs.glyph_part_ignore_regex,
                           pargs.profile_file, pargs.layout_row_profile_file,
                           pargs.glyph_dir, pargs.layout_file,
                           pargs.glyph_map_file, pargs.unit_length,
                           pargs.global_x_offset, pargs.global_y_offset)

    if pargs.output_location == '-':
        print(svg)
    else:
        with open(pargs.output_location, 'w+') as f:
            print(svg, file=f)

    return 0


if __name__ == '__main__':
    exit(main(argv))
