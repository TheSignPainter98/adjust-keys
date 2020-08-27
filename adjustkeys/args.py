# Copyright (C) Edward Jones

from .blender_available import blender_available
from .exceptions import AdjustKeysGracefulExit
from .log import die
from .sanitise_args import arg_inf, sanitise_args
from .util import dict_union
from .version import version
from .yaml_io import read_yaml, write_yaml
from argparse import ArgumentParser, Namespace
from functools import reduce
from multiprocessing import cpu_count
from os import getcwd
from os.path import abspath, dirname, exists, join, normpath
from pathlib import Path
from platform import system
if blender_available():
    from bpy import data

description: str = 'This is a python script which generates layouts of keycaps and glyphs for (automatic) import into Blender! Gone will be the days of manually placing caps into the correct locations and spending hours fixing alignment problems of glyphs on individual keys - simply specify the layout you want using the JSON output of KLE to have the computer guide the caps into the mathematically-correct locations. This script can be used to create a single source of truth for glyph alignment on caps, so later changes and fixes can be more easily propagated.'

# Arguments
adjustkeys_path:str = normpath(abspath(dirname(__file__)))
if adjustkeys_path.endswith('adjustkeys'):
    adjustkeys_path = normpath(adjustkeys_path[:-len('adjustkeys')])
if adjustkeys_path.endswith('adjustkeys-bin'):
    adjustkeys_path = normpath(adjustkeys_path[:-len('adjustkeys-bin')])
default_opts_file: str = 'opts.yml'
args: [dict] = [{
    'dest': 'cap_dir',
    'short': '-K',
    'long': '--key-cap-dir',
    'action': 'store',
    'help': 'specify the directory containing the keycap obj files',
    'metavar': 'file',
    'default': join(adjustkeys_path, 'profiles', 'kat'),
    'label': 'Keycap model folder',
    'type': str,
    'str-type': 'dir'
}, {
    'dest': 'cap_unit_length',
    'short': '-u',
    'long': '--cap-unit-length',
    'action': 'store',
    'help':
    'Specify the length of one unit (in mm) for use when placing keycap models',
    'metavar': 'float',
    'default': 19.05,
    'label': 'Keycap model unit length',
    'type': float,
    'soft-min': 0.0,
    'soft-max': 100.0
}, {
    'dest': 'cap_x_offset',
    'short': '-x',
    'long': '--cap-x-offset',
    'action': 'store',
    'help': 'global offset which moves every keycap to the right',
    'metavar': 'float',
    'default': 0.525,
    'label': 'Keycap global x-offset',
    'type': float,
    'soft-min': 0.0,
    'soft-max': 100.0
}, {
    'dest': 'cap_y_offset',
    'short': '-y',
    'long': '--cap-y-offset',
    'action': 'store',
    'help': 'global offset which moves every keycap downwards',
    'metavar': 'float',
    'default': 0.525,
    'label': 'Keycap global z-offset',
    'type': float,
    'soft-min': 0,
    'soft-max': 100.0
}, {
    'dest': 'colour_map_file',
    'short': '-c',
    'long': '--colour-map',
    'action': 'store',
    'help': 'specify the location of the colour map file',
    'metavar': 'file',
    'default': join(adjustkeys_path, 'examples', 'colour-map.yml'),
    'label': 'Colour map file',
    'type': str,
    'str-type': 'file'
}, {
    'dest': 'do_check_update',
    'short': '-Vu',
    'long': '--check-updates',
    'action': 'store_true',
    'help': 'Forcibly for updates',
    'default': False,
    'type': bool
}, {
    'dest': 'global_x_offset',
    'short': '-X',
    'long': '--glyph-x-offset',
    'action': 'store',
    'help': 'global offset which moves every glyph to the right',
    'metavar': 'float',
    'default': 0.0,
    'label': 'Glyph global x-offset',
    'type': float,
    'soft-min': 0.0,
    'soft-max': 100.0
}, {
    'dest': 'global_y_offset',
    'short': '-Y',
    'long': '--glyph-y-offset',
    'action': 'store',
    'help': 'global offset which moves every glyph downwards',
    'metavar': 'float',
    'default': 0.0,
    'label': 'Glyph global z-offset',
    'type': float,
    'soft-min': 0.0,
    'soft-max': 0.0
}, {
    'dest': 'glyph_dir',
    'short': '-G',
    'long': '--glyph-dir',
    'action': 'store',
    'help': 'specify the directory containing the svg glyphs',
    'metavar': 'file',
    'default': adjustkeys_path,
    'label': 'Glyph folder',
    'type': str,
    'str-type': 'dir'
}, {
    'dest': 'glyph_map_file',
    'short': '-M',
    'long': '--glyph-map',
    'action': 'store',
    'help':
    'specify the file containing the mapping from glyphs to the key ids they will appear upon',
    'metavar': 'file',
    'default': join(adjustkeys_path, 'examples', 'menacing-map.yml'),
    'label': 'Glyph-keycap mapping file',
    'type': str,
    'str-type': 'file'
}, {
    'dest': 'glyph_part_ignore_regex',
    'short': '-i',
    'long': '--ignore-id',
    'action': 'store',
    'help':
    'Specify an id for which nodes and their children should be removed from an input glyph svg',
    'metavar': 'id',
    'default': 'cap-guide',
    'label': 'Glyph node strip regex',
    'type': str
}, {
    'dest': 'glyph_unit_length',
    'short': '-U',
    'long': '--glyph-unit-length',
    'action': 'store',
    'help':
    'Specify the length of one unit (in svg units) for use when placing glyphs',
    'metavar': 'float',
    'default': 292.0,
    'label': 'Glyph unit length',
    'type': float,
    'soft-min': 0.0,
    'soft-max': 1000.0
}, {
    'dest': 'homing_keys',
    'short': '-H',
    'long': '--homing',
    'nargs': '+',
    'metavar': 'key',
    'help': 'Specify which keys are homing keys in a comma-separated list',
    'default': 'f,j',
    'label': 'Homing keys',
    'type': str
}, {
    'dest':
    'iso_enter_glyph_pos',
    'short':
    '-I',
    'long':
    '--iso-enter-glyph-pos',
    'action':
    'store',
    'choices': [
        'centre', 'top-left', 'top-centre', 'top-right', 'bottom-centre',
        'body-centre'
    ],
    'help':
    'Specify the glyph location on an ISO enter key',
    'metavar':
    'pos',
    'default':
    'body-centre',
    'label':
    'ISO-enter glyph location',
    'type':
    str
}, {
    'dest': 'layout_file',
    'short': '-L',
    'long': '--layout',
    'action': 'store',
    'help': 'specify the file containing the layout to use',
    'metavar': 'file',
    'default': join(adjustkeys_path, 'examples', 'layout.yml'),
    'label': 'KLE layout JSON file',
    'type': str,
    'str-type': 'file'
}, {
    'dest': 'layout_row_profile_file',
    'short': '-R',
    'long': '--profile-row-file',
    'action': 'store',
    'help':
    'specify the file containing the mapping from rows of the layout to their profile row',
    'metavar': 'file',
    'default': join(adjustkeys_path, 'examples', 'layout_row_profiles.yml'),
    'label': 'Layout row-profile list file',
    'type': str,
    'str-type': 'file'
}, {
    'dest': 'list_cap_models',
    'short': '-Sc',
    'long': '--show-cap-models',
    'action': 'store_true',
    'help': 'Output a list of known keycap names read form the input files',
    'default': False,
    'label': 'List keycap model names',
    'type': bool,
    'label': 'Print found keycap models',
    'op': True
}, {
    'dest': 'list_cap_names',
    'short': '-Sn',
    'long': '--show-cap-names',
    'action': 'store_true',
    'help': 'Output a list of known keycap names read form the input files',
    'default': False,
    'label': 'List keycap mapping-names',
    'type': bool,
    'label': 'Print known keycap labels',
    'op': True
}, {
    'dest': 'list_glyphs',
    'short': '-Sg',
    'long': '--show-glyph-names',
    'action': 'store_true',
    'help': 'Output a list of known glyphs read from the input files',
    'default': False,
    'label': 'List found glyph names',
    'type': bool,
    'label': 'Print known glyph names',
    'op': True
}, {
    'dest': 'no_adjust_caps',
    'short': '-Nc',
    'long': '--no-adjust-caps',
    'action': 'store_true',
    'help': "Don't perform cap adjustment",
    'default': False,
    'label': "Don't produce aligned keycaps",
    'type': bool
}, {
    'dest': 'no_adjust_glyphs',
    'short': '-Ng',
    'long': '--no-adjust-glyphs',
    'action': 'store_true',
    'help': "Don't perform glyph adjustment",
    'default': False,
    'label': "Don't produce aligned glyphs",
    'type': bool
}, {
    'dest': 'no_check_update',
    'short': '-Vn',
    'long': '--no-check-updates-version',
    'action': 'store_true',
    'help': 'Forcibly for updates',
    'default': False,
    'type': bool
}, {
    'dest': 'no_shrink_wrap',
    'short': '-Ns',
    'long': '--no-shrink-wrap',
    'action': 'store_true',
    'help': "Don't shrink wrap the adjusted glyphs and to the adjusted caps",
    'default': False,
    'label': "Don't shrink-wrap glyphs onto keys",
    'type': bool
}, {
    'dest': 'nprocs',
    'short': '-j',
    'long': '--jobs',
    'action': 'store',
    'help':
    'Specify the number of threads which are used in concurrent sections to improve performance',
    'metavar': 'n',
    'default': 2 * cpu_count(),
    'label': 'CPU cores to use',
    'type': int,
    'min': 0,
    'max': 4 * cpu_count()
}, {
    'dest': 'opt_file',
    'short': '-@',
    'long': '--args',
    'action': 'store',
    'help':
    'specify a YAML option file to be take read initial argument values from',
    'metavar': 'file',
    'default': None,
    'type': str,
    'str-type': 'file'
}, {
    'dest': 'output_dir',
    'short': '-o',
    'long': '--output',
    'action': 'store',
    'help':
    'Specify the location of any output files, if blender is loaded, this is just a temporary location and files are cleaned away before the script finishes',
    'metavar': 'dir',
    'default': adjustkeys_path,
    'type': str,
    'str-type': 'dir'
}, {
    'dest': 'output_prefix',
    'short': '-O',
    'long': '--output-prefix',
    'action': 'store',
    'help': 'Specify a prefix to be applied to all output names',
    'metavar': 'str',
    'default': 'adjustedkeys',
    'type': str
}, {
    'dest': 'print_opts_yml',
    'short': '-#',
    'long': '--print-opts-yml',
    'action': 'store_true',
    'help': 'Print the current options values in the YAML format for configuration purposes and exit',
    'default': False,
    'type': bool,
    'label': 'Print opts.yml',
    'op': True
}, {
    'dest': 'profile_file',
    'short': '-C',
    'long': '--centres',
    'action': 'store',
    'help': 'specify the profile-centres YAML file to use',
    'metavar': 'file',
    'default': join(adjustkeys_path, 'profiles', 'kat', 'centres.yml'),
    'label': 'Keycap profile centre file',
    'type': str,
    'str-type': 'file'
}, {
    'dest': 'shrink_wrap_offset',
    'short': '-d',
    'long': '--shrink-wrap-offset',
    'action': 'store',
    'help': 'Specify the offset above the surfave used by the shrink wrap',
    'metavar': 'mm',
    'default': 0.0001,
    'label': 'Shrink wrap offset',
    'type': float,
    'soft-min': 0.0,
    'soft-max': 1.0,
}, {
    'dest': 'suppress_update_checking',
    'short': '-Vs',
    'long': '--suppress-update-checking',
    'action': 'store_true',
    'help': 'Forcibly for updates',
    'default': False,
    'type': bool
}, {
    'dest': 'svg_units_per_mm',
    'short': '-D',
    'long': '--svg-upmm',
    'action': 'store',
    'help': 'Specify the number of units per mm used in the svg images',
    'metavar': 'float',
    'default': 90.0 / 25.4,
    'arg_inf_msg': '(90dpi)',
    'label': 'SVG units per mm',
    'type': float,
    'soft-min': 0.0,
    'soft-max': 100.0,
}, {
    'dest': 'verbosity',
    'short': '-v',
    'long': '--verbose',
    'action': 'store',
    'help': 'Output verbosely',
    'metavar': 'int',
    'default': 0,
    'type': int,
    'choices': [0, 1, 2]
}, {
    'dest': 'show_version',
    'short': '-V',
    'long': '--version',
    'action': 'version',
    'version': version,
    'help': 'Print current version and exit',
    'default': False,
    'type': bool,
    'label': 'Print version',
    'op': True
}, {
    'dest': 'show_help',
    'short': '-h',
    'long': '--help',
    'action': 'help',
    'help': 'Print help message and exit',
    'default': False,
    'type': bool
}]

arg_dict: dict = {a['dest']: a for a in args if 'dest' in a}
configurable_args: [dict] = list(
    sorted(filter(lambda a: 'dest' in a and 'label' in a and 'op' not in a, args),
           key=lambda a:
           ('choices' in a, str(a['type']), a['str-type']
            if 'str-type' in a else 'raw', a['label'])))
op_args:[dict] = list(filter(lambda a: 'dest' in a and 'label' in a and 'op' in a and a['op'], args))

home:str = Path.home()
progname:str = 'adjustkeys'
install_dir:str = { 'Linux': join(home, '.local', 'lib', 'adjustkeys'), 'Windows': join(home, 'Library', 'Application Support', 'Adjustkeys'), 'Darwin': join(home, 'AppData', 'Local', 'Adjustkeys') }[system()]

##
# @brief Parse commandline arguments
# If an error occurs, the an exception is raised
#
# @param args:[str] A list of commandline arguments, including argv[0], the program name
#
# @return A namespace of options
def parse_args(iargs: tuple) -> Namespace:
    ap: ArgumentParser = ArgumentParser(description=description, add_help=False)

    # Generate the argument parser
    for arg in args:
        ap.add_argument(
            arg['short'], arg['long'],
            **dict_union(
                {
                    k: v
                    for k, v in arg.items()
                    if k in ['dest', 'action', 'metavar', 'version'] + (['type'] if arg['type'] != bool else [])
                },
                {'help': arg['help'] + arg_inf(arg)} if 'help' in arg else {}))

    # Sanitise and obtain parsed arguments
    pargs: dict
    iargs = sanitise_args('adjustglyphs', iargs)
    if type(iargs) == dict:
        pargs = iargs
    else:
        pargs: dict = ap.parse_args(iargs[1:]).__dict__

    # Obtain yaml arguments
    yargs: dict = {}
    if 'opt_file' in pargs and pargs['opt_file'] is not None:
        if exists(pargs['opt_file']):
            yargs = read_yaml(pargs['opt_file'])
        else:
            die('Failed to find options file "%s"' % pargs['opt_file'])
    elif exists(default_opts_file):
        raw_yargs = read_yaml(default_opts_file)
        yargs = raw_yargs if type(raw_yargs) == dict else {}

    dargs = { a['dest']: a['default'] for a in args if 'dest' in a }
    rargs: dict = dict_union_ignore_none(dict_union_ignore_none(dargs, yargs), pargs)
    rargs = dict(map(lambda p: (p[0], arg_dict[p[0]]['type'](p[1])), rargs.items()))
    checkResult:str = check_args(rargs)
    if checkResult is not None:
        ap.print_usage()
        die(checkResult)

    npargs:Namespace = Namespace(**rargs)
    if npargs.show_version:
        ap.print_version()
        raise AdjustKeysGracefulExit()
    elif npargs.show_help:
        ap.print_help()
        raise AdjustKeysGracefulExit()
    return npargs


def check_args(args: dict) -> 'Maybe str':
    items: [[str, object]] = args.items()
    if all(map(lambda a: type(a[1]) == arg_dict[a[0]]['type'], items)) and all(map( lambda a: 'choices' not in arg_dict[a[0]] or a[1] in arg_dict[a[0]] ['choices'], items)):
        return None
    wrong_types:[str] = list(map(lambda a: 'Expected %s value for %s but got %s' %(str(arg_dict[a[0]]['type']), arg_dict[a[0]]['dest'], str(a[1])), filter(lambda a: type(a[1]) != arg_dict[a[0]]['type'], items)))
    wrong_choices:[str] = list(map(lambda a: 'Argument %s only accepts %s but got %s' % (arg_dict[a[0]]['dest'], ', '.join(list(map(str, arg_dict[a[0]]['choices']))), str(a[1])), filter(lambda a: 'choices' in arg_dict[a[0]] and a[1] not in arg_dict[a[0]]['choices'], items)))

    return '\n'.join(wrong_types + wrong_choices)


def dict_union_ignore_none(a: dict, b: dict) -> dict:
    return dict(a, **dict(filter(lambda p: p[1] is not None, b.items())))
