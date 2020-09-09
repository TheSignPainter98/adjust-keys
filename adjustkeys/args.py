# Copyright (C) Edward Jones

from .arg_defs import args, arg_dict, default_opts_file
from .blender_available import blender_available
from .exceptions import AdjustKeysGracefulExit
from .lazy_import import LazyImport
from .log import die
from .sanitise_args import arg_inf, sanitise_args
from .util import dict_union
from .version import version
from .yaml_io import read_yaml, write_yaml
from argparse import ArgumentParser, Namespace
from functools import reduce
from multiprocessing import cpu_count
from os.path import exists, join
if blender_available():
    data = LazyImport('bpy', 'data')

description: str = 'This is a python script which generates layouts of keycaps and glyphs for (automatic) import into Blender! Gone will be the days of manually placing caps into the correct locations and spending hours fixing alignment problems of glyphs on individual keys - simply specify the layout you want using the JSON output of KLE to have the computer guide the caps into the mathematically-correct locations. This script can be used to create a single source of truth for glyph alignment on caps, so later changes and fixes can be more easily propagated.'

progname:str = 'adjustkeys'

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
    for arg in list(sorted(args, key=lambda arg: arg['short'].lower())):
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
    if 'opt_file' not in pargs or pargs['opt_file'] is None:
        pargs['opt_file'] = 'None'

    # Obtain yaml arguments
    yargs: dict = {}
    if pargs['opt_file'] != 'None':
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
        print(version)
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
