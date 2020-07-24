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

from argparse import ArgumentParser, Namespace
from log import printe
from multiprocessing import cpu_count
from os.path import exists
from sanitise_args import arg_inf, sanitise_args
from util import dict_union
from yaml_io import read_yaml, write_yaml

version:str = 'v1.0.0'


##
# @brief Parse commandline arguments
# If an error occurs, the program immediately exits.
#
# @param args:[str] A list of commandline arguments, including argv[0], the program name
#
# @return A namespace of options
def parse_args(args:[str]) -> Namespace:
    ap:ArgumentParser = ArgumentParser()

    # Default values
    dargs:dict = {
            'opt_file': 'opts.yml',
            'verbosity': 0,
            'output_dir': '.',
            'output_prefix': 'adjustedkeys',
            'cap_unit_length': 19.05,
            'cap_x_offset': 0.525,
            'cap_y_offset': 0.525,
            'cap_dir': 'profiles/kat/',
            'layout_file': 'examples/layout.yml',
            'layout_row_profile_file': 'examples/layout_row_profiles.yml',
            #  'output_location': 'adjusted-glyphs.svg',
            'listGlyphs': 0,
            'listKeys': 0,
            'glyph_unit_length': 292.0,
            'glyph_part_ignore_regex': 'cap-guide',
            'global_x_offset': 0.0,
            'global_y_offset': 0.0,
            'profile_file': 'profiles/kat/centres.yml',
            'glyph_dir': '.',
            'glyph_map_file': 'examples/menacing-map.yml',
            'nprocs': 2 * cpu_count()
        }

    ap.add_argument('-V', '--version', action='version', version=version)
    ap.add_argument('-v', '--verbose', action='store', dest='verbosity', type=int, help='Output verbosely' + arg_inf(dargs, 'verbosity'))
    ap.add_argument('-o', '--output', action='store', dest='output_dir', help='Specify the location of any output files, if blender is loaded, this is just a temporary location and files are cleaned away before the script finishes' + arg_inf(dargs, 'output_dir'))
    ap.add_argument('-O', '--output-prefix', action='store', dest='output_prefix', help='Specify a prefix to be applied to all output names' + arg_inf(dargs, 'output_prefix'))
    ap.add_argument('-g', '--list-glyphs', action='store_true', dest='listGlyphs', help='Output a list of known glyphs read from the input files' + arg_inf(dargs, 'listGlyphs'))
    ap.add_argument('-k', '--list-keys', action='store_true', dest='listKeys', help='Output a list of known key names read form the input files' + arg_inf(dargs, 'listKeys'))
    ap.add_argument('-@', '--args', action='store', dest='opt_file', help='specify a YAML option file to be take read initial argument values from (default: %s)' % dargs['opt_file'], metavar='file')
    ap.add_argument('-u', '--cap-unit-length', action='store', type=float, dest='cap_unit_length', help='Specify the length of one unit (in mm) for use when placing keycap models' + arg_inf(dargs, 'cap_unit_length'), metavar='num')
    ap.add_argument('-U', '--glyph-unit-length', action='store', type=float, dest='glyph_unit_length', help='Specify the length of one unit (in svg units) for use when placing glyphs' + arg_inf(dargs, 'glyph_unit_length'), metavar='num')
    ap.add_argument('-i', '--ignore-id', action='store', type=str, dest='glyph_part_ignore_regex', help='Specify an id for which nodes and their children should be removed from an input glyph svg' + arg_inf(dargs, 'glyph_part_ignore_regex'), metavar='id')
    ap.add_argument('-X', '--glyph-x-offset', action='store', type=float, dest='global_x_offset', help='global offset which moves every glyph to the right' + arg_inf(dargs, 'global_x_offset'), metavar='num')
    ap.add_argument('-Y', '--glyph-y-offset', action='store', type=float, dest='global_y_offset', help='global offset which moves every glyph downwards' + arg_inf(dargs, 'global_y_offset'), metavar='num')
    ap.add_argument('-x', '--cap-x-offset', action='store', type=float, dest='cap_x_offset', help='global offset which moves every keycap to the right' + arg_inf(dargs, 'cap_x_offset'), metavar='num')
    ap.add_argument('-y', '--cap-y-offset', action='store', type=float, dest='cap_y_offset', help='global offset which moves every keycap downwards' + arg_inf(dargs, 'cap_y_offset'), metavar='num')
    ap.add_argument('-C', '--centres', action='store', dest='profile_file', help='specify the profile-centres YAML file to use' + arg_inf(dargs, 'profile_file'), metavar='file')
    ap.add_argument('-K', '--key-cap-dir', action='store', dest='cap_dir', help='specify the directory containing the keycap obj files' + arg_inf(dargs, 'cap_dir'), metavar='file')
    ap.add_argument('-G', '--glyph-dir', action='store', dest='glyph_dir', help='specify the directory containing the svg glyphs' + arg_inf(dargs, 'glyph_dir'), metavar='file')
    ap.add_argument('-L', '--layout', action='store', dest='layout_file', help='specify the file containing the layout to use' + arg_inf(dargs, 'layout_file'), metavar='file')
    ap.add_argument('-R', '--profile-row-file', action='store', dest='layout_row_profile_file', help='specify the file containing the mapping from rows of the layout to their profile row' + arg_inf(dargs, 'layout_row_profile_file'), metavar='file')
    ap.add_argument('-M', '--glyph-map', action='store', dest='glyph_map_file', help='specify the file containing the mapping from glyphs to the key ids they will appear upon' + arg_inf(dargs, 'glyph_map_file'), metavar='file')
    ap.add_argument('-j', '--jobs', action='store', dest='nprocs', type=int, help='Specify the number of threads which are used in concurrent sections to improve performance' + arg_inf(dargs, 'nprocs'))

    # Sanitise and obtain parsed arguments
    args = sanitise_args('adjustglyphs', args)
    pargs:dict = ap.parse_args(args[1:]).__dict__

    # Obtain yaml arguments
    yargs:dict = {}
    if 'opt_file' in pargs and pargs['opt_file'] is not None:
        if exists(pargs['opt_file']):
            yargs = read_yaml(pargs['opt_file'])
        else:
            printe('Failed to find options file %s' % pargs['opt_file'])
            exit(1)
    elif exists(dargs['opt_file']):
        yargs = read_yaml(dargs['opt_file'])

    return Namespace(**dict_union_ignore_none(dict_union_ignore_none(dargs, yargs), pargs))

def dict_union_ignore_none(a:dict, b:dict) -> dict:
    return dict(a, **dict(filter(lambda p: p[1] is not None, b.items())))
