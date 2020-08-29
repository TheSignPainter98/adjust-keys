# Copyright (C) Edward Jones

from .args import Namespace
from .log import printi, printw
from .version import version
from os.path import exists

metaDataUrl:str = 'https://api.github.com/repos/TheSignPainter98/adjust-keys/releases/latest'

def update_available(pargs: Namespace) -> bool:
    return pargs.check_update and check_update(False)

def check_update(pedanticCheck:bool) -> bool:
    from grequests import get as gget, map as gmap
    from yaml import safe_load, FullLoader
    resp:Response = gmap([gget(url=metaDataUrl)])[0]
    if resp:
        parsedResp:dict = safe_load(resp.text)
        if 'tag_name' in parsedResp:
            printi('Latest version is %s, current version is %s' %(parsedResp['tag_name'], version))
            return version_is_outdated(version, parsedResp['tag_name'])
    printw('Failed to find out the name of the latest version from github')
    return False

def version_is_outdated(vc:str, vu:str) -> bool:
    if not vc or not vu:
        return False
    return tuple(map(int, vc[1:].split('.'))) < tuple(map(int, vu[1:].split('.')))
