# Copyright (C) Edward Jones

from .path import adjustkeys_path
from .version import version
from os.path import join

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
    'dest': 'check_update',
    'short': '-Vu',
    'long': '--check-updates',
    'action': 'store_true',
    'help': "Check for Adjustkeys updates (requires internet connection)",
    'default': False,
    'type': bool,
    'label': "Check for updates",
    'op': True
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
    'dest': 'fatal_warnings',
    'short': '-E',
    'long': '--fatal-errors',
    'action': 'store_true',
    'help': 'Treat any warnings as fatal, halting execution immediately',
    'default': False,
    'type': bool,
}, {
    'dest': 'glyph_dir',
    'short': '-G',
    'long': '--glyph-dir',
    'action': 'store',
    'help': 'specify the directory containing the svg glyphs',
    'metavar': 'file',
    'default': join(adjustkeys_path, 'glyphs', 'red-hat-display'),
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
    'default': join(adjustkeys_path, 'examples', 'ansi-example-map.yml'),
    'label': 'Glyph map file',
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
    'label': 'Glyph node id removal regex',
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
        'top-left', 'top-centre', 'top-right', 'middle-centre', 'middle-right',
        'bottom-centre', 'bottom-right'
    ],
    'help':
    'Specify the glyph position on an ISO enter key',
    'metavar':
    'pos',
    'default':
    'middle-centre',
    'label':
    'ISO-enter glyph position',
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
    'dest': 'list_cap_models',
    'short': '-Sc',
    'long': '--show-cap-models',
    'action': 'store_true',
    'help': 'Output a list of known keycap names read form the input files',
    'default': False,
    'label': 'List keycap model names',
    'type': bool,
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
    'dest': 'no_apply_colour_map',
    'short': '-NC',
    'long': '--no-apply-colour_map',
    'action': 'store',
    'help': "Don't apply colour materials to the keycaps (colouring in KLE layout file will still override this)",
    'default': False,
    'label': "Don't apply the colour map",
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
    'dest': 'opt_file',
    'short': '-@',
    'long': '--args',
    'action': 'store',
    'help':
    'specify a YAML option file to read initial argument values from',
    'metavar': 'file',
    'default': None,
    'type': str,
    'str-type': 'file',
    'label': 'YAML option file'
}, {
    'dest': 'print_opts_yml',
    'short': '-#',
    'long': '--print-opts-yml',
    'action': 'store_true',
    'help': 'Print the current options values in the YAML format for configuration purposes and exit',
    'default': False,
    'type': bool,
    'label': 'List current options in YAML',
    'op': True
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
    'help': 'Control how much logging output is given, 0 for minimal, 2 for everything',
    'metavar': 'int',
    'default': 1,
    'label': 'Console-output verbosity',
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
    'label': 'Show version',
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

