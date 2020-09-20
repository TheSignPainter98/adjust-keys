#!/usr/bin/python3

from adjustkeys.log import die
from adjustkeys.util import concat, list_diff, safe_get
from functools import reduce
from os.path import exists, join, dirname
from sys import exit, argv


def main(args: [str]) -> int:
    if len(args) < 2:
        die('Please give at least one argument, got %s' %(len(args) - 1))

    mainName:str = args[1]
    if mainName.endswith('.in'):
        mainName = mainName[:-3]
    if mainName.endswith('.py'):
        mainName = mainName[:-3]
    print(' '.join(internal_dependencies(mainName)))

    return 0

def internal_dependencies(file:str) -> [str]:
    return list(filter(exists, get_project_deps(file)))

def external_dependencies(file:str) -> [str]:
    return set(map(lambda p: p[:-3].split('.')[0], filter(lambda f: not exists(f), get_project_deps(file))))

def get_project_deps(file:str) -> [str]:
    seen:[str] = [file]
    toExplore:[str] = [file]
    while toExplore != []:
        seen = list(set(seen + toExplore))
        newDeps:{str} = list(reduce(concat, map(get_deps, toExplore)))
        toExplore = list_diff(newDeps, seen)
    return list(reduce(concat, map(lambda p: [p, p + '.in'], map(lambda d: d + '.py', seen))))

def get_deps(mod: str) -> [str]:
    fname: str = mod.replace('.', '/') + '.py'
    code: [str]
    if exists(fname):
        with open(fname, 'r') as i:
            code = i.readlines()
    elif exists(fname + '.in'):
        with open(fname + '.in', 'r') as i:
            code = i.readlines()
    else:
        return []

    import_lines: [str] = list(
        filter(
            lambda l: safe_get(l, 0) == 'import' or (safe_get(l, 0) == 'from' and safe_get(l, 2) == 'import'),
            list(map(lambda l: l.strip().split(' '), code))))
    return list(map(lambda i: resolve_name(mod, i), map(lambda l: l[1], import_lines)))

def resolve_name(mod:str, dep:str) -> str:
    if mod.endswith('adjustkeys_addon') and dep.startswith('.'):
        dep = dep[len('.adjustkeys'):]
    if not dep.startswith('.'):
        return dep
    return join(dirname(mod), dep[1:])


if __name__ == '__main__':
    exit(main(argv))
