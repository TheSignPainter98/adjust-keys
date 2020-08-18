# Copyright (C) Edward Jones

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from blender_available import blender_available
if blender_available():
    from bpy import data
from exceptions import AdjustKeysGracefulExit
from log import die
from multiprocessing import cpu_count
from os import getcwd
from os.path import dirname, exists, join
from path import fexists
from platform import system
from pathlib import Path
from sanitise_args import arg_inf, sanitise_args
from util import dict_union
from version import version
from yaml_io import read_yaml, write_yaml

description:str = 'This is a python script which generates layouts of keycaps and glyphs for (automatic) import into Blender! Gone will be the days of manually placing caps into the correct locations and spending hours fixing alignment problems of glyphs on individual keys - simply specify the layout you want using the JSON output of KLE to have the computer guide the caps into the mathematically-correct locations. This script can be used to create a single source of truth for glyph alignment on caps, so later changes and fixes can be more easily propagated.'

home:str = Path.home()
install_dir:str = { 'Linux': join(home, '.local', 'lib', 'adjustkeys'), 'Windows': join(home, 'Library', 'Application Support', 'Adjustkeys'), 'Darwin': join(home, 'AppData', 'Local', 'Adjustkeys') }[system()]

##
# @brief Parse commandline arguments
# If an error occurs, the an exception is raised
#
# @param args:[str] A list of commandline arguments, including argv[0], the program name
#
# @return A namespace of options
def parse_args(args:[str]) -> Namespace:
    ap:ArgumentParser = ArgumentParser(description=description, add_help=False)

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
            'list_glyphs': False,
            'list_cap_names': False,
            'list_cap_models': False,
            'glyph_unit_length': 292.0,
            'glyph_part_ignore_regex': 'cap-guide',
            'global_x_offset': 0.0,
            'global_y_offset': 0.0,
            'profile_file': 'profiles/kat/centres.yml',
            'glyph_dir': '.',
            'glyph_map_file': 'examples/menacing-map.yml',
            'nprocs': 2 * cpu_count(),
            'shrink_wrap_offset': 0.0001,
            'svg_units_per_mm': 90.0 / 25.4,
            'no_adjust_caps': False,
            'no_adjust_glyphs': False,
            'no_shrink_wrap': False,
            'iso_enter_glyph_pos': 'body-centre',
            'do_check_update': False,
            'no_check_update': False,
            'suppress_update_checking': False,
            'homing_keys': [ 'f', 'j' ],
            'colour_map_file': 'examples/colour-map.yml',
            'path': ':'.join([ install_dir, getcwd() ] + ([data.filepath] if blender_available() and data.filepath else [])),
            'print_opts_yml': False,
            'show_version': False,
            'show_help': False
        }

    ap.add_argument('-@', '--args', action='store', dest='opt_file', help='specify a YAML option file to be take read initial argument values from (default: %s)' % dargs['opt_file'], metavar='file')
    ap.add_argument('-c', '--colour-map', action='store', dest='colour_map_file', help='specify the location of the colour map file' + arg_inf(dargs, 'colour_map_file'), metavar='file')
    ap.add_argument('-C', '--centres', action='store', dest='profile_file', help='specify the profile-centres YAML file to use' + arg_inf(dargs, 'profile_file'), metavar='file')
    ap.add_argument('-d', '--shrink-wrap-offset', action='store', dest='shrink_wrap_offset', type=float, help='Specify the offset above the surfave used by the shrink wrap' + arg_inf(dargs, 'shrink_wrap_offset'), metavar='mm')
    ap.add_argument('-D', '--svg-dpi', action='store', dest='svg_units_per_mm', type=float, help='Specify the number of units per mm used in the svg images' + arg_inf(dargs, 'svg_units_per_mm', msg='(90dpi)'), metavar='float')
    ap.add_argument('-G', '--glyph-dir', action='store', dest='glyph_dir', help='specify the directory containing the svg glyphs' + arg_inf(dargs, 'glyph_dir'), metavar='file')
    ap.add_argument('-h', '--help', action='help', help='Show help message and exit' + arg_inf(dargs, 'show_help'))
    ap.add_argument('-H', '--homing', nargs='+', dest='homing_keys', metavar='key', help='Specify which keys are homing keys' + arg_inf(dargs, 'homing_keys'))
    ap.add_argument('-i', '--ignore-id', action='store', type=str, dest='glyph_part_ignore_regex', help='Specify an id for which nodes and their children should be removed from an input glyph svg' + arg_inf(dargs, 'glyph_part_ignore_regex'), metavar='id')
    ap.add_argument('-I', '--iso-enter-glyph-pos', action='store', choices=['centre', 'top-left', 'top-centre', 'top-right', 'bottom-centre', 'body-centre'], dest='iso_enter_glyph_pos', help='Specify the glyph location on an ISO enter key' + arg_inf(dargs, 'iso_enter_glyph_pos'), metavar='pos')
    ap.add_argument('-j', '--jobs', action='store', dest='nprocs', type=int, help='Specify the number of threads which are used in concurrent sections to improve performance' + arg_inf(dargs, 'nprocs'), metavar='n')
    ap.add_argument('-K', '--key-cap-dir', action='store', dest='cap_dir', help='specify the directory containing the keycap obj files' + arg_inf(dargs, 'cap_dir'), metavar='file')
    ap.add_argument('-L', '--layout', action='store', dest='layout_file', help='specify the file containing the layout to use' + arg_inf(dargs, 'layout_file'), metavar='file')
    ap.add_argument('-M', '--glyph-map', action='store', dest='glyph_map_file', help='specify the file containing the mapping from glyphs to the key ids they will appear upon' + arg_inf(dargs, 'glyph_map_file'), metavar='file')
    ap.add_argument('-Nc', '--no-adjust-caps', action='store_true', dest='no_adjust_caps', help="Don't perform cap adjustment" + arg_inf(dargs, 'no_adjust_caps'))
    ap.add_argument('-Ng', '--no-adjust-glyphs', action='store_true', dest='no_adjust_glyphs', help="Don't perform glyph adjustment" + arg_inf(dargs, 'no_adjust_glyphs'))
    ap.add_argument('-Ns', '--no-shrink-wrap', action='store_true', dest='no_shrink_wrap', help="Don't shrink wrap the adjusted glyphs and to the adjusted caps" + arg_inf(dargs, 'no_shrink_wrap'))
    ap.add_argument('-o', '--output', action='store', dest='output_dir', help='Specify the location of any output files, if blender is loaded, this is just a temporary location and files are cleaned away before the script finishes' + arg_inf(dargs, 'output_dir'), metavar='dir')
    ap.add_argument('-O', '--output-prefix', action='store', dest='output_prefix', help='Specify a prefix to be applied to all output names' + arg_inf(dargs, 'output_prefix'), metavar='str')
    ap.add_argument('-P', '--path', action='store', dest='path', help='Specify a different search path---a colon-separated list of directories which are searched every time a file is read. Default holds the current working directory (e.g. of Blender if opened through that), the directory in which adjustkeys is stored and the directory of the currently-open .blend file if available' + arg_inf(dargs, 'path'), metavar='path')
    ap.add_argument('-R', '--profile-row-file', action='store', dest='layout_row_profile_file', help='specify the file containing the mapping from rows of the layout to their profile row' + arg_inf(dargs, 'layout_row_profile_file'), metavar='file')
    ap.add_argument('-Sg', '--show-glyph-names', action='store_true', dest='list_glyphs', help='Output a list of known glyphs read from the input files' + arg_inf(dargs, 'list_glyphs'))
    ap.add_argument('-Sn', '--show-cap-names', action='store_true', dest='list_cap_names', help='Output a list of known keycap names read form the input files' + arg_inf(dargs, 'list_cap_names'))
    ap.add_argument('-Sc', '--show-cap-models', action='store_true', dest='list_cap_models', help='Output a list of known keycap names read form the input files' + arg_inf(dargs, 'list_cap_models'))
    ap.add_argument('-u', '--cap-unit-length', action='store', type=float, dest='cap_unit_length', help='Specify the length of one unit (in mm) for use when placing keycap models' + arg_inf(dargs, 'cap_unit_length'), metavar='float')
    ap.add_argument('-U', '--glyph-unit-length', action='store', type=float, dest='glyph_unit_length', help='Specify the length of one unit (in svg units) for use when placing glyphs' + arg_inf(dargs, 'glyph_unit_length'), metavar='float')
    ap.add_argument('-v', '--verbose', action='store', dest='verbosity', type=int, help='Output verbosely' + arg_inf(dargs, 'verbosity'), metavar='int')
    ap.add_argument('-V', '--version', action='version', version=version, help="Show program's version number and exit" + arg_inf(dargs, 'show_version'))
    ap.add_argument('-Vu', '--check-updates', action='store_true', dest='do_check_update', help='Forcibly for updates' + arg_inf(dargs, 'do_check_update'))
    ap.add_argument('-Vn', '--no-check-updates-version', action='store_true', dest='no_check_update', help='Forcibly for updates' + arg_inf(dargs, 'no_check_update'))
    ap.add_argument('-Vs', '--suppress-update-checking', action='store_true', dest='suppress_update_checking', help='Forcibly for updates' + arg_inf(dargs, 'suppress_update_checking'))
    ap.add_argument('-x', '--cap-x-offset', action='store', type=float, dest='cap_x_offset', help='global offset which moves every keycap to the right' + arg_inf(dargs, 'cap_x_offset'), metavar='float')
    ap.add_argument('-X', '--glyph-x-offset', action='store', type=float, dest='global_x_offset', help='global offset which moves every glyph to the right' + arg_inf(dargs, 'global_x_offset'), metavar='float')
    ap.add_argument('-y', '--cap-y-offset', action='store', type=float, dest='cap_y_offset', help='global offset which moves every keycap downwards' + arg_inf(dargs, 'cap_y_offset'), metavar='float')
    ap.add_argument('-Y', '--glyph-y-offset', action='store', type=float, dest='global_y_offset', help='global offset which moves every glyph downwards' + arg_inf(dargs, 'global_y_offset'), metavar='float')
    ap.add_argument('-#', '--opts-yml', action='store_true', dest='print_opts_yml', help='Print the current options values in the YAML format for configuration purposes and exit' + arg_inf(dargs, 'print_opts_yml'))

    # Sanitise and obtain parsed arguments
    args = sanitise_args('adjustkeys', args)
    pargs:dict = ap.parse_args(args[1:]).__dict__

    # Obtain yaml arguments
    yargs:dict = {}
    if 'opt_file' in pargs and pargs['opt_file'] is not None:
        if fexists(pargs['opt_file']):
            yargs = read_yaml(pargs['opt_file'])
        else:
            die('Failed to find options file "%s"' % pargs['opt_file'])
    elif fexists(dargs['opt_file']):
        raw_yargs = read_yaml(dargs['opt_file'])
        yargs = raw_yargs if type(raw_yargs) == dict else {}

    npargs:Namespace = Namespace(**dict_union_ignore_none(dict_union_ignore_none(dargs, yargs), pargs))
    if npargs.show_version:
        ap.print_version()
        raise AdjustKeysGracefulExit()
    elif npargs.show_help:
        ap.print_help()
        raise AdjustKeysGracefulExit()
    return npargs

def dict_union_ignore_none(a:dict, b:dict) -> dict:
    return dict(a, **dict(filter(lambda p: p[1] is not None, b.items())))
