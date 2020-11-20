# Copyright (C) Edward Jones

from .path import adjustkeys_path
from .version import version
from os.path import join

default_opts_file: str = 'opts.yml'
args: [dict] = [{
    'dest': 'adaptive_subsurf',
    'short': '-Fn',
    'long': '--no-adaptive-subsurf',
    'action': 'store_false',
    'help': 'Adaptively apply subdivision surface modifiers to the glyphs-parts by using size to determine the number of levels. Each glyph part has a number of subdivisions applied in the range [0...m], where m is (by context) either the max viewport or render subdivision level values',
    'default': True,
    'type': bool,
    'label': 'Adaptively apply subsurf modifiers',
}, {
    'dest': 'alignment',
    'short': '-a',
    'long': '--alignment',
    'action': 'store',
    'help': 'Specify the alignment of glyphs on caps',
    'metavar': 'direction',
    'default': 'middle-centre',
    'choices': [
       'top-left', 'top-centre', 'top-right',
       'middle-left', 'middle-centre', 'middle-right',
       'bottom-left', 'bottom-centre', 'bottom-right'
    ],
    'type': str,
    'label': 'Alignment direction'
}, {
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
    'dest':
    'iso_enter_glyph_pos',
    'short':
    '-I',
    'long':
    '--iso-enter-glyph-pos',
    'action':
    'store',
    'choices': [
        'top-left', 'top-centre', 'top-right',
        'middle-left', 'middle-centre', 'middle-right',
        'bottom-left', 'bottom-centre', 'bottom-right'
    ],
    'help':
    'Specify the alignment on an ISO enter key',
    'metavar':
    'pos',
    'default':
    'middle-centre',
    'label':
    'ISO-enter alignment',
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
    'dest': 'legended_caps',
    'short': '-H',
    'long': '--legended-caps',
    'action': 'store_true',
    'help': 'Assume legends are part of the keycap models (currently incompatible with colour maps)',
    'default': False,
    'label': 'Legends in keycap models',
    'type': bool,
    'implies': [
        '¬apply_colour_map',
        '¬shrink_wrap',
        '¬adjust_glyphs',
    ]
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
    'dest': 'adjust_caps',
    'short': '-Nc',
    'long': '--no-adjust-caps',
    'action': 'store_false',
    'help': 'Import keycap models and correctly adjust their positions',
    'default': True,
    'label': 'Import keycap meshes',
    'type': bool
}, {
    'dest': 'adjust_glyphs',
    'short': '-Ng',
    'long': '--no-adjust-glyphs',
    'action': 'store_false',
    'help': 'Import glyphs and correctly adjust their positions',
    'default': True,
    'label': 'Import glyph curves',
    'type': bool
}, {
    'dest': 'apply_colour_map',
    'short': '-NC',
    'long': '--no-apply-colour_map',
    'action': 'store_false',
    'help': 'Apply the colour map file’s rules to the keycaps and glyphs (colouring in KLE layout file still overrides this)',
    'default': True,
    'label': 'Apply colour map',
    'type': bool
}, {
    'dest': 'shrink_wrap',
    'short': '-Ns',
    'long': '--no-shrink-wrap',
    'action': 'store_false',
    'help': "Subdivide and shrink wrap glyph models onto the keycaps",
    'default': True,
    'label': 'Shrink wrap glyphs to keys',
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
    'dest': 'scaling',
    'short': '-s',
    'long': '--scaling',
    'action': 'store',
    'help': 'A factor by which to scale the output',
    'metavar': 'factor',
    'default': 1.0,
    'label': 'Output scaling',
    'type': float,
    'soft-min': 0.001,
    'soft-max': 1000.0,
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
    'dest': 'subsurf_viewport_levels',
    'short': '-Fv',
    'long': '--subsurf-viewport-levels',
    'action': 'store',
    'help': 'Set the levels of the subdivision surface modifier applied ot glyph parts in the viewport',
    'metavar': 'levels',
    'default': 2,
    'label': 'Subsurf mod viewport levels',
    'type': int,
    'min': 0,
    'max': 11
}, {
    'dest': 'subsurf_render_levels',
    'short': '-Fr',
    'long': '--subsurf-render-levels',
    'action': 'store',
    'help': 'Set the levels of the subdivision surface modifier applied ot glyph parts in renders',
    'metavar': 'levels',
    'default': 3,
    'label': 'Subsurf mod render levels',
    'type': int,
    'min': 0,
    'max': 11
}, {
    'dest': 'subsurf_quality',
    'short': '-Fq',
    'long': '--subsurf-quality',
    'action': 'store',
    'help': 'Set the quality parameter of the subdivision surface modifier applied to all glyph-parts',
    'metavar': 'quality',
    'default': 3,
    'label': 'Subsurf mod quality',
    'type': int,
    'min': 0,
    'max': 10
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

