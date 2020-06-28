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

from adjust_keys import adjust_keys
from args import parse_args, Namespace
from sys import argv, exit
from yaml_io import write_yaml


##
# @brief Entry point function, should be treated as the first thing called
#
# @param args:[str] Command line arguments
#
# @return Zero if and only if the program is to exit successfully
def main(args: [str]) -> int:
    pargs: Namespace = parse_args(args)
    positions: [dict] = adjust_keys(
        pargs.verbosity, pargs.profile_file, pargs.layout_row_profile_file,
        pargs.glyph_offset_file, pargs.layout_file, pargs.glyph_map_file,
        pargs.unit_length, pargs.delta_x, pargs.delta_y, pargs.global_x_offset,
        pargs.global_y_offset)

    write_yaml(
        '-',
        list(
            map(
                lambda m: {
                    'glyph': m['glyph'],
                    'pos-x': m['pos-x'],
                    'pos-y': m['pos-y'],
                    'src': m['src']
                }, positions)))

    return 0


if __name__ == '__main__':
    exit(main(argv))
