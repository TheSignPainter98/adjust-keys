# Copyright (C) Edward Jones

from .log import die
from .util import concat, dict_union, flatten_list
from functools import reduce
from sys import argv


def sanitise_args(pname: str, args) -> list:
    global argv
    if type(args) == tuple:
        args = list(args)
    if args == ['']:
        args = []
    args = flatten_list(args)
    if type(args) == list and all(map(lambda a: type(a) == str, args)):
        args = list(reduce(concat, map(args_from_str, args), []))
    elif type(args) == list and all(map(lambda a: type(a) == dict, args)):
        # If dictionaries, just unite them and return that, they cannot be further sanitised (we ignore petty issues such as the existence of files here :P)
        return dict(reduce(dict_union, args, {}))
    elif type(args) == str:
        args = args_from_str(args)
    else:
        die('Unknown argument type, %s received, please use a list of (lists of) strings or just a single string'
                %(str(type(args)) if type(args) == list else ', '.join(set(filter(lambda a: type(a) != str, args)))))
    # Put executable name on the front if it is absent (e.g. if called from python with only the arguments specified)
    if len(args) == 0 or args[0] != argv[0]:
        if len(args) == 0:
            argv.append(pname)
        elif not argv[0].lower().startswith('blender'):
            argv[0] = pname
        args = [argv[0]] + list(args)

    return args


def args_from_str(s: str) -> [str]:
    args: [str] = []
    arg: str = ''
    i: int = 0
    ignoreOne: bool = False
    matchChar: str = None
    lenS: int = len(s)
    while i < lenS:
        if s[i] == '\\' and matchChar != "'":
            ignoreOne = True
        elif s[i] in ['"', "'"] and not ignoreOne:
            if matchChar is None:
                matchChar = s[i]
            elif matchChar == s[i]:
                matchChar = None
            else:
                arg += s[i]
        elif matchChar is None:
            if ignoreOne:
                arg += s[i]
                ignoreOne = False
            elif s[i] == ' ':
                args.append(arg)
                while i < lenS and s[i] == ' ':
                    i += 1
                i -= 1
                arg = ''
            else:
                arg += s[i]
        else:
            arg += s[i]
            ignoreOne = False
        i += 1

    if matchChar is not None:
        die('Failed to find matching "%s"' % matchChar)
    elif ignoreOne:
        die('Expected another character after being told to ignore one (\\)')
    elif arg != '':
        args.append(arg)

    return args


def arg_inf(arg:dict) -> str:
    if 'default' in arg:
        return ' (default: %s%s, yaml-option-file-key: %s)' % (arg['default'], ' ' + arg['arg_inf_msg'] if 'arg_inf_msg' in arg else '', arg['dest'])
    return ''
