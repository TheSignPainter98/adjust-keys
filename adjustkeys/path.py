# Copyright (C) Edward Jones

from os import walk as owalk
from os.path import abspath, dirname, join, normpath
from tempfile import NamedTemporaryFile

adjustkeys_path:str = normpath(abspath(dirname(__file__)))
if adjustkeys_path.endswith('adjustkeys'):
    adjustkeys_path = normpath(adjustkeys_path[:-len('adjustkeys')])
if adjustkeys_path.endswith('adjustkeys-bin'):
    adjustkeys_path = normpath(adjustkeys_path[:-len('adjustkeys-bin')])

def walk(dname:str) -> [str]:
    ret:[str] = []
    for (r,_,fs) in owalk(dname):
        ret.extend(map(lambda f: join(r,f), fs))
    return ret

def get_temp_file_name() -> str:
    name:str
    with NamedTemporaryFile() as f:
        name = f.name
    return name
