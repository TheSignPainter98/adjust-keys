# Copyright (C) Edward Jones

from argparse import ArgumentParser, Namespace
from log import printe
from multiprocessing import cpu_count
from os.path import exists
from sanitise_args import arg_inf, sanitise_args
from util import dict_union
from version import version
from yaml_io import read_yaml, write_yaml

description:str = 'This is a python script which generates layouts of keycaps and glyphs for (automatic) import into Blender! Gone will be the days of manually placing caps into the correct locations and spending hours fixing alignment problems of glyphs on individual keys - simply specify the layout you want using the JSON output of KLE to have the computer guide the caps into the mathematically-correct locations. This script can be used to create a single source of truth for glyph alignment on caps, so later changes and fixes can be more easily propagated.'

# Arguments
default_opts_file:str = 'opts.yml'
args:[dict] = [
        { 'dest': 'cap_dir', 'short': '-K', 'long': '--key-cap-dir', 'action': 'store', 'help': 'specify the directory containing the keycap obj files', 'metavar': 'file', 'default': 'profiles/kat/' },
        { 'dest': 'cap_unit_length', 'short': '-u', 'long': '--cap-unit-length', 'action': 'store', 'type': float, 'help': 'Specify the length of one unit (in mm) for use when placing keycap models', 'metavar': 'float', 'default': 19.05 },
        { 'dest': 'cap_x_offset', 'short': '-x', 'long': '--cap-x-offset', 'action': 'store', 'type': float, 'help': 'global offset which moves every keycap to the right', 'metavar': 'float', 'default': 0.525 },
        { 'dest': 'cap_y_offset', 'short': '-y', 'long': '--cap-y-offset', 'action': 'store', 'type': float, 'help': 'global offset which moves every keycap downwards', 'metavar': 'float', 'default': 0.525 },
        { 'dest': 'colour_map_file', 'short': '-c', 'long': '--colour-map', 'action': 'store', 'help': 'specify the location of the colour map file', 'metavar': 'file', 'default': './examples/colour-map.yml' },
        { 'dest': 'do_check_update', 'short': '-Vu','long': '--check-updates', 'action': 'store_true', 'help': 'Forcibly for updates', 'default': False },
        { 'dest': 'global_x_offset', 'short': '-X', 'long': '--glyph-x-offset', 'action': 'store', 'type': float, 'help': 'global offset which moves every glyph to the right', 'metavar': 'float', 'default': 0.0 },
        { 'dest': 'global_y_offset', 'short': '-Y', 'long': '--glyph-y-offset', 'action': 'store', 'type': float, 'help': 'global offset which moves every glyph downwards', 'metavar': 'float', 'default': 0.0 },
        { 'dest': 'glyph_dir', 'short': '-G', 'long': '--glyph-dir', 'action': 'store', 'help': 'specify the directory containing the svg glyphs', 'metavar': 'file', 'default': '.' },
        { 'dest': 'glyph_map_file', 'short': '-M', 'long': '--glyph-map', 'action': 'store', 'help': 'specify the file containing the mapping from glyphs to the key ids they will appear upon', 'metavar': 'file', 'default': 'examples/menacing-map.yml' },
        { 'dest': 'glyph_part_ignore_regex', 'short': '-i', 'long': '--ignore-id', 'action': 'store', 'type': str, 'help': 'Specify an id for which nodes and their children should be removed from an input glyph svg', 'metavar': 'id', 'default': 'cap-guide' },
        { 'dest': 'glyph_unit_length', 'short': '-U', 'long': '--glyph-unit-length', 'action': 'store', 'type': float, 'help': 'Specify the length of one unit (in svg units) for use when placing glyphs', 'metavar': 'float', 'default': 292.0 },
        { 'dest': 'homing_keys', 'short': '-H', 'long': '--homing', 'nargs': '+', 'metavar': 'key', 'help': 'Specify which keys are homing keys', 'default': [ 'f', 'j' ] },
        { 'dest': 'iso_enter_glyph_pos', 'short': '-I', 'long': '--iso-enter-glyph-pos', 'action': 'store', 'choices': ['centre', 'top-left', 'top-centre', 'top-right', 'bottom-centre', 'body-centre'], 'help': 'Specify the glyph location on an ISO enter key', 'metavar': 'pos', 'default': 'body-centre' },
        { 'dest': 'layout_file', 'short': '-L', 'long': '--layout', 'action': 'store', 'help': 'specify the file containing the layout to use', 'metavar': 'file', 'default': 'examples/layout.yml' },
        { 'dest': 'layout_row_profile_file', 'short': '-R', 'long': '--profile-row-file', 'action': 'store', 'help': 'specify the file containing the mapping from rows of the layout to their profile row', 'metavar': 'file', 'default': 'examples/layout_row_profiles.yml' },
        { 'dest': 'list_cap_models', 'short': '-Sc','long': '--show-cap-models', 'action': 'store_true', 'help': 'Output a list of known keycap names read form the input files', 'default': False },
        { 'dest': 'list_cap_names', 'short': '-Sn','long': '--show-cap-names', 'action': 'store_true', 'help': 'Output a list of known keycap names read form the input files', 'default': False },
        { 'dest': 'list_glyphs', 'short': '-Sg','long': '--show-glyph-names', 'action': 'store_true', 'help': 'Output a list of known glyphs read from the input files', 'default': False },
        { 'dest': 'no_adjust_caps', 'short': '-Nc','long': '--no-adjust-caps', 'action': 'store_true', 'help': "Don't perform cap adjustment", 'default': False },
        { 'dest': 'no_adjust_glyphs', 'short': '-Ng','long': '--no-adjust-glyphs', 'action': 'store_true', 'help': "Don't perform glyph adjustment", 'default': False },
        { 'dest': 'no_check_update', 'short': '-Vn','long': '--no-check-updates-version', 'action': 'store_true', 'help': 'Forcibly for updates', 'default': False },
        { 'dest': 'no_shrink_wrap', 'short': '-Ns','long': '--no-shrink-wrap', 'action': 'store_true', 'help': "Don't shrink wrap the adjusted glyphs and to the adjusted caps", 'default': False },
        { 'dest': 'nprocs', 'short': '-j', 'long': '--jobs', 'action': 'store', 'type': int, 'help': 'Specify the number of threads which are used in concurrent sections to improve performance', 'metavar': 'n', 'default': 2 * cpu_count() },
        { 'dest': 'opt_file', 'short': '-@', 'long': '--args', 'action': 'store', 'help': 'specify a YAML option file to be take read initial argument values from', 'metavar': 'file', 'default': None },
        { 'dest': 'output_dir', 'short': '-o', 'long': '--output', 'action': 'store', 'help': 'Specify the location of any output files, if blender is loaded, this is just a temporary location and files are cleaned away before the script finishes', 'metavar': 'dir', 'default': '.' },
        { 'dest': 'output_prefix', 'short': '-O', 'long': '--output-prefix', 'action': 'store', 'help': 'Specify a prefix to be applied to all output names', 'metavar': 'str', 'default': 'adjustedkeys' },
        { 'dest': 'profile_file', 'short': '-C', 'long': '--centres', 'action': 'store', 'help': 'specify the profile-centres YAML file to use', 'metavar': 'file', 'default': 'profiles/kat/centres.yml' },
        { 'dest': 'shrink_wrap_offset', 'short': '-d', 'long': '--shrink-wrap-offset', 'action': 'store', 'type': float, 'help': 'Specify the offset above the surfave used by the shrink wrap', 'metavar': 'mm', 'default': 0.0001 },
        { 'dest': 'suppress_update_checking', 'short': '-Vs','long': '--suppress-update-checking', 'action': 'store_true', 'help': 'Forcibly for updates', 'default': False },
        { 'dest': 'svg_units_per_mm', 'short': '-D', 'long': '--svg-upmm', 'action': 'store', 'type': float, 'help': 'Specify the number of units per mm used in the svg images', 'metavar': 'float', 'default': 90.0 / 25.4, 'arg_inf_msg': '(90dpi)' },
        { 'dest': 'verbosity', 'short': '-v', 'long': '--verbose', 'action': 'store', 'type': int, 'help': 'Output verbosely', 'metavar': 'int', 'default': 0 },
        { 'short': '-V', 'long': '--version', 'action': 'version', 'version': version }
    ]


##
# @brief Parse commandline arguments
# If an error occurs, the program immediately exits.
#
# @param args:[str] A list of commandline arguments, including argv[0], the program name
#
# @return A namespace of options
def parse_args(iargs:[str]) -> Namespace:
    ap:ArgumentParser = ArgumentParser(description=description)

    # Generate the argument parser
    for arg in args:
        ap.add_argument(arg['short'], arg['long'], **dict_union({ k:v for k,v in arg.items() if k in ['dest', 'action', 'type', 'metavar', 'version' ]}, { 'help': arg['help'] + arg_inf(arg) } if 'help' in arg else {}))

    # Sanitise and obtain parsed arguments
    iargs = sanitise_args('adjustglyphs', iargs)
    pargs:dict = ap.parse_args(iargs[1:]).__dict__

    # Obtain yaml arguments
    yargs:dict = {}
    if 'opt_file' in pargs and pargs['opt_file'] is not None:
        if exists(pargs['opt_file']):
            yargs = read_yaml(pargs['opt_file'])
        else:
            printe('Failed to find options file %s' % pargs['opt_file'])
            exit(1)
    elif exists(default_opts_file):
        yargs = read_yaml(default_opts_file)

    dargs = { a['dest']: a['default'] for a in args if 'dest' in a }
    return Namespace(**dict_union_ignore_none(dict_union_ignore_none(dargs, yargs), pargs))

def dict_union_ignore_none(a:dict, b:dict) -> dict:
    return dict(a, **dict(filter(lambda p: p[1] is not None, b.items())))
