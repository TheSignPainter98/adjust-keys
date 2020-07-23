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
from sanitise_args import arg_inf, sanitise_args
from util import dict_union
from yaml_io import read_yaml, write_yaml

version:str = '0.1.0'

##
# @brief Parse commandline arguments
# If an error occurs, the program immediately exits.
#
# @param args:[str] A list of commandline arguments, including argv[0], the program name
#
# @return A namespace of options
def parse_args(args:[str]) -> Namespace:
    ap:ArgumentParser = ArgumentParser()

    # Default arguments
    dargs:dict = {
            'opt_file': 'cap-opts.yml',
            'verbosity': 0,
            'output_dir': '.',
            'unit_length': 19.05,
            'x_offset': 0.525,
            'y_offset': 0.525,
            'plane': 'y',
            'cap_dir': '.',
            'layout_file': 'examples/layout.yml',
            'layout_row_profile_file': 'examples/layout_row_profiles.yml',
            'move_to_origin': False
        }

    ap.add_argument('-V', '--version', action='version', version=version)
    ap.add_argument('-v', '--verbose', action='store', dest='verbosity', type=int, help='Output verbosely' + arg_inf(dargs, 'verbosity'))
    ap.add_argument('-o', '--output-dir', action='store', dest='output_dir', help='Specify directory to write to output or' + arg_inf(dargs, 'output_dir'))
    ap.add_argument('-O', '--move-to-origin', action='store_true', dest='move_to_origin', help='If set, translate the respective input files\' data to the origin' + arg_inf(dargs, 'move_to_origin'))
    ap.add_argument('-@', '--args', action='store', dest='opt_file', help='specify a YAML option file to be take read initial argument values from (default: %s)' % dargs['opt_file'], metavar='file')
    ap.add_argument('-u', '--unit-length', action='store', type=float, dest='unit_length', help='Specify the length of one unit, that is, the width of a 1u keycap' + arg_inf(dargs, 'unit_length'), metavar='num')
    ap.add_argument('-x', '--x-offset', action='store', type=float, dest='x_offset', help='global offset which moves every element to the right' + arg_inf(dargs, 'x_offset'), metavar='num')
    ap.add_argument('-y', '--y-offset', action='store', type=float, dest='y_offset', help='global offset which moves every element downwards' + arg_inf(dargs, 'y_offset'), metavar='num')
    #  ap.add_argument('-p', '--plane', action='store', type=str, dest='plane', help='specify the canonical basis vector along which normal-plane the layout will be arranged (choices: x, y, z, default: z)', metavar='num')
    ap.add_argument('-K', '--key-cap-dir', action='store', dest='cap_dir', help='specify the directory containing the keycap obj files' + arg_inf(dargs, 'cap_dir'), metavar='file')
    ap.add_argument('-L', '--layout', action='store', dest='layout_file', help='specify the file containing the layout to use' + arg_inf(dargs, 'layout_file'), metavar='file')
    ap.add_argument('-R', '--profile-row-file', action='store', dest='layout_row_profile_file', help='specify the file containing the mapping from rows of the layout to their profile row' + arg_inf(dargs, 'layout_row_profile_file'), metavar='file')

    # Sanitise and obtain parsed arguments
    args = sanitise_args('adjustcaps', args)
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
