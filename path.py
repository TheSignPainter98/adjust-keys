# Copyright (C) Edward Jones

from os import walk as owalk
from os.path import join

def walk(dname:str) -> [str]:
    ret:[str] = []
    for (r,_,fs) in owalk(dname):
        ret.extend(map(lambda f: join(r,f), fs))
    return ret
