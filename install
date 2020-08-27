#!/usr/bin/python3

from argparse import ArgumentParser, Namespace
from errno import ENOTDIR
from os import makedirs, remove, symlink, system
from os.path import exists, isdir, join
from pathlib import Path
from platform import system
from shutil import copy, copytree, rmtree
from subprocess import call
from sys import argv, exit

home:str = Path.home()
quiet:bool = False
no_error_prompt:bool = False
install_data:dict = {
        'Linux': {
            'install-loc': join(home, '.local', 'lib', 'adjustkeys'),
            'bin-loc': join(home, '.local', 'bin', 'adjustkeys')
        },
        'Darwin': {
            'install-loc': join(home, 'Library', 'Application Support', 'Adjustkeys'),
            'bin-loc': None
        },
        'Windows': {
            'install-loc': join(home, 'AppData', 'Local', 'Adjustkeys'),
            'bin-loc': None
        }
    }

def main(args) -> int:
    global quiet
    global no_error_prompt
    pargs:Namespace = parse_args(args[1:])
    quiet = pargs.quiet
    no_error_prompt = pargs.no_error_prompt
    pname:str = system()
    rc:int

    # Install pip dependencies
    if not pargs.no_python_update and not pargs.uninstall:
        rc = install_modules()
        if rc:
            return rc

    # Check OS is supported
    if pname not in install_data:
        log('Sorry, platform "%s" is not supported, please file a bug report' % pname)
        return 1

    idata:dict = install_data[pname]
    rc = uninstall(idata)
    if rc or pargs.uninstall:
        return rc
    return install(idata)

def parse_args(args:[str]) -> Namespace:
    ap:ArgumentParser = ArgumentParser()
    ap.add_argument('-q', '--quiet', action='store_true', dest='quiet', help='Suppress all but error output')
    ap.add_argument('-p', '--no-python-module-install', action='store_true', dest='no_python_update', help="Don't update python modules")
    ap.add_argument('-x', '--exit-on-failure', action='store_true', dest='no_error_prompt', help="Suppress the 'Press any key to continue...' prompt at an error")
    ap.add_argument('-u', '--uninstall', action='store_true', dest='uninstall', help='Remove installation of adjustkeys, skips the (re)installation step')
    return ap.parse_args(args)

def install_modules():
    log('Installing python dependencies...')
    rc:int =  call('pip3 install -qq -r requirements.txt'.split(' '))
    if rc:
        return rc
    log('Installed python dependencies ✓')

def uninstall(data:dict) -> int:
    log('Checking for existing installation...')
    exists_bin_loc:bool = exists(data['bin-loc'])
    exists_install_loc:bool = exists(data['install-loc'])
    if exists_bin_loc or exists_install_loc:
        log('Removing existing installation...')
        if exists_bin_loc and data['bin-loc']:
            rm(data['bin-loc'])
        if exists_install_loc:
            rm(data['install-loc'])
    else:
        log('\t(None found)')
    return 0

def install(data:dict) -> int:
    # Copy binary into suitable location
    cp('.', data['install-loc'])
    # Make a symbolic link to the executable
    if data['bin-loc']:
        sym(join(data['install-loc'], 'adjustkeys'), data['bin-loc'])
    log('All done!')
    return 0

def mkdir(dname:str):
    log('Making directory "%s"...' % dname, end=' ')
    makedirs(dname, exist_ok=True)
    log('✓')

def cp(src:str, dest:str):
    log('Copying "%s" -> "%s"...' % (src, dest), end=' ')
    try:
        copytree(src, dest)
    except OSError as ose:
        if ose.errno == ENOTDIR:
            copy(src, dest)
        else:
            raise
    log('✓')

def sym(src:str, dest:str):
    log('Creating symbolic link "%s" ->> "%s"...' %(dest, src), end=' ')
    symlink(src, dest)
    log('✓')

def rm(name:str):
    log('Deleting file "%s"...' % name, end=' ')
    if isdir(name):
        rmtree(name)
    else:
        remove(name)
    log('✓')

def log(*args, **kwargs):
    if not quiet:
        print(*args, **kwargs)

if __name__ == '__main__':
    try:
        rc:int = main(argv)
        if rc:
            input('Press any key to continue...')
        exit(rc)
    except KeyboardInterrupt:
        exit(1)
    except Exception as ex:
        print('ERROR:', ex)
        if not no_error_prompt:
            input('Press any key to continue...')
