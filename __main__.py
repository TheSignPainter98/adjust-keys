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
from layout import Layout
from log import init_logging, printe, printi
from sys import argv, exit
from yaml_io import read_yaml, write_yaml
from util import nat_join

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
    #  layout = Layout(read_yaml(pargs.layout_file))
    glyph_map = read_yaml(pargs.glyph_map_file)
    #  print(glyph_map[0])
    glyph_rel = list(map(lambda m: { 'key': m[0], 'glyph': m[1] }, glyph_map.items()))

    write_yaml('-', glyph_rel)

    return 0

if __name__ == '__main__':
    exit(main(argv))
