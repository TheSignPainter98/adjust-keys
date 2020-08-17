# Copyright (C) Edward Jones

from log import die
from os import walk
from os.path import exists, join
from util import get_only

path:[str] = []

def init_path(fpath:str):
    global path
    npath:[str] = fpath.split(':')
    if npath == []:
        die('Got invalid path: ', npath)
    path = npath

def find_file(fname:str, no_file_msg:str, multiple_file_msg:str) -> str:
    es:[str] = list(filter(exists, map(lambda p: join(p, fname), path)))
    return get_only(es, no_file_msg, multiple_file_msg)

def fexists(fname:str) -> bool:
    return list(filter(exists, map(lambda p: join(p, fname), path))) != []

def fwalk(dname:str) -> [str]:
    ret:[str] = []
    for d in list(filter(exists, [join(p, dname) for p in path])):
        for (r,_,fs) in walk(d):
            ret.extend(list(filter(exists, map(lambda f: join(r,f), fs))))
    return set(ret)

def fopen(fname:str, no_file_msg:str, multiple_file_msg:str, *args, **kwargs) -> 'file':
    return open(find_file(fname, no_file_msg, multiple_file_msg), *args, **kwargs)
