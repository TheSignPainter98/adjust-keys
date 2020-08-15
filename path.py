# Copyright (C) Edward Jones

from log import die
from os.path import exists, join
from util import get_only

path:[str] = []

def init_path(fpath:str):
    global path
    npath:[str] = fpath.split(':')
    if npath == []:
        die('Got invalid path: ', npath)
    path = npath

def find_file(fname:str) -> str:
    es:[str] = list(filter(exists, map(lambda p: join(p, fname), path)))
    return get_only(es)

def fopen(fname:str, *args, **kwargs) -> 'file':
    return open(find_file(fname), *args, **kwargs)
