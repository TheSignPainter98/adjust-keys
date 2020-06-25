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
from os.path import exists
from util import union
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

    ap.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Output verbosely')
    ap.add_argument('-q', '--quiet', action='store_true', dest='quiet', help='Suppress messages more than usual')
    ap.add_argument('-@', '--args', action='store', dest='opt_file', help='specify a YAML option file to be take read initial argument values from (default: opts.yml)', default='opts.yml', metavar='file')
    ap.add_argument('-P', '--profile', action='store', dest='profile_file', help='specify the prile YAML file to use (default: kat.yml)', default='kat.yml', metavar='file')
    ap.add_argument('-O', '--glyph-offsets', action='store', dest='glyph_offset_file', help='specify the file containing offsets for each glyph from the center of a keys (default: glyph-offsets.yaml)', default='glyph-offsets.yml', metavar='file')
    ap.add_argument('-L', '--layout', action='store', dest='layout_file', help='specify the file containing the layout to use (default: layout.yaml)', default='layout.yml', metavar='file')
    ap.add_argument('-M', '--glyph-map', action='store', dest='glyph_map_file', help='specify the file containing the mapping from glyphs to the key ids they will appear upon (default: glyph-map.yml)', default='glyph-map.yml', metavar='file')
    ap.add_argument('-x', '--global-x-offset', action='store', type=float, dest='global_x_offset', help='global offset which moves every element to the right (default: 0.0)', default=0.0, metavar='num')
    ap.add_argument('-y', '--global-y-offset', action='store', type=float, dest='global_y_offset', help='global offset which moves every element downwards (default: 0.0)', default=0.0, metavar='num')
    ap.add_argument('-u', '--unit-length', action='store', type=float, dest='unit_length', help='Specify the length of one unit, that is, the width of a 1u keycap(default: 1.0)', default=1.0, metavar='num')

    # Obtain parsed arguments
    pargs:dict = ap.parse_args(args[1:]).__dict__

    # Obtain yaml arguments
    yargs:dict = {}
    if exists(pargs['opt_file']):
        yargs = read_yaml(pargs['opt_file'])
    elif pargs.opt_file != 'opts.yml':
        printe('Failed to find options file %s' % pargs.opt_file)
        exit(1)

    return Namespace(**union(yargs, pargs))