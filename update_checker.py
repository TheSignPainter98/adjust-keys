# Copyright (C) Edward Jones

from args import Namespace
from os.path import exists
from log import printi, printw

metaDataUrl:str = 'https://api.github.com/repos/TheSignPainter98/adjust-keys/releases/latest'
updateSuppressorFile: str = '.no_adjustkeys_update'
noUpdateMsg: str = '\n'.join([
        "Hello.", "",
        "If you're reading this in a file called '%s,' it means that" % updateSuppressorFile,
        "adjustkeys isn't doesn't check for updates and hence won't annoy you with a",
        "message for a new one every time you run it, which fair enough.  That this file",
        "exists at all is a small amount of laziness on my part as it avoids needing to",
        "set up package manager entries for various platforms for this program.",
        "", "If you want to check for updates, just delete this file.", "",
        "While I have you here though, did you ever hear the tragedy of Darth Plagueis",
        "The Wise? I thought not. It’s not a story the Jedi would tell you. It’s a Sith",
        "legend. Darth Plagueis was a Dark Lord of the Sith, so powerful and so wise he",
        "could use the Force to influence the midichlorians to create life… He had such",
        "a knowledge of the dark side that he could even keep the ones he cared about",
        "from dying. The dark side of the Force is a pathway to many abilities some",
        "consider to be unnatural. He became so powerful… the only thing he was afraid",
        "of was losing his power, which eventually, of course, he did. Unfortunately, he",
        "taught his apprentice everything he knew, then his apprentice killed him in his",
        "sleep. Ironic. He could save others from death, but not himself."
    ])


def update_available(pargs: Namespace) -> bool:
    if pargs.do_check_update:
        printi('Checking for updates...')
        return check_update(True)
    elif pargs.no_check_update:
        printi('Not checking for updates')
        return False
    elif pargs.suppress_update_checking:
        if not exists(updateSuppressorFile):
            with open(updateSuppressorFile, 'w+') as f:
                print(noUpdateMsg, file=f)
        printi('Update checking has been suppressed')
        return False
    elif not exists(updateSuppressorFile):
        return check_update(False)

def check_update(pedanticCheck:bool) -> bool:
    from grequests import get as gget, map as gmap
    from version import version
    from yaml import safe_load, FullLoader
    resp:Response = gmap([gget(url=metaDataUrl)])[0]
    if resp:
        parsedResp:dict = safe_load(resp.text)
        if 'tag_name' in parsedResp:
            printi('Latest version is %s, current version is %s' %(parsedResp['tag_name'], version))
            if pedanticCheck:
                print('asdf')
                return version != parsedResp['tag_name']
            else:
                print('fdsa')
                return version_is_outdated(version, parsedResp['tag_name'])
    printw('Failed to find out the name of the latest version from github')
    return False

def version_is_outdated(vc:str, vu:str) -> bool:
    return tuple(map(int, vc[1:].split('.')))[:-1] < tuple(map(int, vu[1:].split('.')))[:-1]
