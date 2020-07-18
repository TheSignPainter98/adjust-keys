# Copyright (C)  Edward Jones
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

from argparse import ArgumentParser, Namespace
from log import printe
from os.path import exists
from util import dict_union
from yaml_io import read_yaml, write_yaml

##
# @brief Parse commandline arguments
# If an error occurs, the program immediately exits.
#
# @param args:[str] A list of commandline arguments, including argv[0], the program name
#
# @return A namespace of options
def parse_args(args:[str]) -> Namespace:
    ap:ArgumentParser = ArgumentParser()

    ap.add_argument('-v', '--verbose', action='store', dest='verbosity', type=int, help='Output verbosely')
    ap.add_argument('-o', '--output', action='store', dest='output_location', help='Specify file to write to output or `-` for stdeout (default: -) ')
    ap.add_argument('-g', '--list-glyphs', action='store_true', dest='listGlyphs', help='Output a list of known glyphs read from the input files')
    ap.add_argument('-k', '--list-keys', action='store_true', dest='listKeys', help='Output a list of known key names read form the input files')
    ap.add_argument('-@', '--args', action='store', dest='opt_file', help='specify a YAML option file to be take read initial argument values from (default: glyph-opts.yml)', metavar='file', default='glyph-opts.yml')
    ap.add_argument('-u', '--unit-length', action='store', type=float, dest='unit_length', help='Specify the length of one unit, that is, the width of a 1u keycap (default: 276.0)', metavar='num')
    ap.add_argument('-i', '--ignore-id', action='store', type=str, dest='glyph_part_ignore_regex', help='Specify an id for which nodes and their children should be removed from an input glyph svg (default: cap-guide)', metavar='id')
    ap.add_argument('-X', '--global-x-offset', action='store', type=float, dest='global_x_offset', help='global offset which moves every element to the right (default: 0.0)', metavar='num')
    ap.add_argument('-Y', '--global-y-offset', action='store', type=float, dest='global_y_offset', help='global offset which moves every element downwards (default: 0.0)', metavar='num')
    ap.add_argument('-P', '--profile', action='store', dest='profile_file', help='specify the profile YAML file to use (default: kat.yml)', metavar='file')
    ap.add_argument('-G', '--glyph-loc', action='store', dest='glyph_dir', help='specify the directory containing the svg glyphs', metavar='file')
    ap.add_argument('-L', '--layout', action='store', dest='layout_file', help='specify the file containing the layout to use (default: layout.yaml)', metavar='file')
    ap.add_argument('-R', '--profile-row-list', action='store', dest='layout_row_profile_file', help='specify the file containing the mapping from rows of the layout to their profile row', metavar='file')
    ap.add_argument('-M', '--glyph-map', action='store', dest='glyph_map_file', help='specify the file containing the mapping from glyphs to the key ids they will appear upon (default: glyph-map.yml)', metavar='file')

    # Obtain parsed arguments
    pargs:dict = ap.parse_args(args[1:]).__dict__

    # Obtain yaml arguments
    yargs:dict = {}
    if exists(pargs['opt_file']):
        yargs = read_yaml(pargs['opt_file'])
    elif pargs['opt_file'] != 'glyph-opts.yml':
        printe('Failed to find options file "%s"' % pargs['opt_file'])
        exit(1)

    return Namespace(**dict_union_ignore_none(yargs, pargs))

def dict_union_ignore_none(a:dict, b:dict) -> dict:
    return dict(a, **dict(filter(lambda p: p[1] is not None, b.items())))